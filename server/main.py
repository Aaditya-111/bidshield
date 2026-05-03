from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fraud.graph_builder import GraphBuilder
from fraud.stats import StatisticalDetector

app = FastAPI(title="BidShield API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize graph
graph = GraphBuilder()

DEMO_BIDS = [
    {"bidder_id": "B1", "amount": 85000000},
    {"bidder_id": "B2", "amount": 72400000},
    {"bidder_id": "B3", "amount": 68000000},
    {"bidder_id": "B4", "amount": 91000000},
    {"bidder_id": "B5", "amount": 72700000},
    {"bidder_id": "B6", "amount": 55000000},
    {"bidder_id": "B7", "amount": 32000000},
    {"bidder_id": "B8", "amount": 48000000},
    {"bidder_id": "B9", "amount": 41000000},
    {"bidder_id": "B10", "amount": 50000000},  
]

@app.get("/demo/stats/benfords-law")
def benfords_law_analysis():
    amounts = [b["amount"] for b in DEMO_BIDS]
    return StatisticalDetector.benfords_law_test(amounts)

@app.get("/demo/stats/bid-clustering")
def statistical_bid_clustering(threshold: float = 1.0):
    return {
        "threshold_percent": threshold,
        "clusters_found": StatisticalDetector.detect_bid_clustering(DEMO_BIDS, threshold)
    }

@app.get("/demo/collusion-risk/{bidder_id}")
def get_collusion_risk(bidder_id: str):

    risk_data = {
        "B2": {
            "graph_signals": ["shared_director", "shared_address", "shared_bank", "shared_phone"],
            "stat_signals": ["bid_clustering"]
        },
        "B5": {
            "graph_signals": ["shared_director", "shared_address", "shared_bank", "shared_phone"],
            "stat_signals": ["bid_clustering"]
        }
    }
    
    signals = risk_data.get(bidder_id, {"graph_signals": [], "stat_signals": []})
    return StatisticalDetector.calculate_collusion_risk(
        bidder_id, 
        signals["graph_signals"], 
        signals["stat_signals"]
    )

@app.get("/demo/full-analysis")
def full_tender_analysis():
    bidders = get_demo_bidders()
    network = graph.get_full_network()
    star_graphs = graph.detect_star_graphs()
    clustering = graph.detect_bid_clustering(0.5)
    benford = StatisticalDetector.benfords_law_test([b["amount"] for b in DEMO_BIDS])
    
    for bidder in bidders["bidders"]:
        if bidder["id"] in ["B2", "B5"]:
            bidder["collusion_risk"] = 79
            bidder["risk_level"] = "HIGH"
            bidder["flags"] = ["Shared director: Rajesh Kumar", "Bid clustering: 0.41% difference"]
    
    return {
        "tender": bidders,
        "fraud_network": network,
        "detections": {
            "star_graphs": star_graphs,
            "bid_clustering": clustering,
            "benfords_law": benford
        },
        "summary": {
            "total_bidders": 10,
            "eligible": 6,
            "ineligible": 3,
            "manual_review": 1,
            "collusion_flags": 2,
            "risk_level": "HIGH"
        }
    }

@app.on_event("shutdown")
def shutdown():
    graph.close()

@app.get("/health")
def health():
    return {"status": "BidShield server running"}

@app.post("/demo/seed")
def seed_database():
    graph.seed_demo_data()
    return {"message": "Demo graph seeded successfully"}

@app.get("/demo/bidders")
def get_demo_bidders():
    return {
        "tender_id": "TNDR-2024-CRPF-001",
        "total_bidders": 10,
        "eligible": 6,
        "ineligible": 3,
        "manual_review": 1,
        "bidders": [
            {"id": "B1", "name": "Alpha Construction", "status": "eligible", "turnover": 85000000, "ocr_confidence": 0.94},
            {"id": "B2", "name": "Beta Infra Ltd", "status": "eligible", "turnover": 72000000, "ocr_confidence": 0.91, "collusion_risk": 79},
            {"id": "B3", "name": "Gamma Builders", "status": "eligible", "turnover": 68000000, "ocr_confidence": 0.89},
            {"id": "B4", "name": "Delta Projects", "status": "eligible", "turnover": 91000000, "ocr_confidence": 0.96},
            {"id": "B5", "name": "Epsilon Corp", "status": "eligible", "turnover": 73000000, "ocr_confidence": 0.92, "collusion_risk": 79},
            {"id": "B6", "name": "Zeta Engineers", "status": "eligible", "turnover": 55000000, "ocr_confidence": 0.88},
            {"id": "B7", "name": "Eta Ventures", "status": "ineligible", "turnover": 32000000, "ocr_confidence": 0.95, "rejection_reason": "Turnover below Rs 5cr threshold"},
            {"id": "B8", "name": "Theta Group", "status": "ineligible", "turnover": 48000000, "ocr_confidence": 0.93, "rejection_reason": "Expired GST certificate"},
            {"id": "B9", "name": "Iota Solutions", "status": "ineligible", "turnover": 41000000, "ocr_confidence": 0.90, "rejection_reason": "Missing audited financials"},
            {"id": "B10", "name": "Kappa Industries", "status": "manual_review", "turnover": None, "ocr_confidence": 0.67, "review_reason": "Certificate photo angled: Rs 4.8cr or 8.4cr?"},
        ]
    }

@app.get("/demo/fraud-network")
def get_fraud_network():
    return graph.get_full_network()

@app.get("/demo/detections/star-graphs")
def detect_star_graphs():
    return {"detections": graph.detect_star_graphs()}

@app.get("/demo/detections/bid-clustering")
def detect_bid_clustering(threshold: float = 0.5):
    return {"detections": graph.detect_bid_clustering(threshold)}