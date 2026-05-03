import math
from collections import Counter
from typing import List, Dict

class StatisticalDetector:
    
    @staticmethod
    def benfords_law_test(values: List[float]) -> Dict:
        
        if not values or len(values) < 10:
            return {"error": "Need at least 10 values for meaningful test"}
        
        first_digits = []
        for v in values:
            if v > 0:
                first_digit = int(str(abs(v))[0])
                if first_digit != 0:
                    first_digits.append(first_digit)
        
        if not first_digits:
            return {"error": "No valid positive values found"}
        
        benford_expected = {
            1: 30.1, 2: 17.6, 3: 12.5, 4: 9.7,
            5: 7.9, 6: 6.7, 7: 5.8, 8: 5.1, 9: 4.6
        }
        
        total = len(first_digits)
        actual_counts = Counter(first_digits)
        
        actual_percentages = {}
        deviations = {}
        chi_square = 0
        
        for digit in range(1, 10):
            count = actual_counts.get(digit, 0)
            actual_pct = (count / total) * 100
            actual_percentages[digit] = round(actual_pct, 2)
            
            expected_pct = benford_expected[digit]
            expected_count = (expected_pct / 100) * total
            
            if expected_count > 0:
                chi_square += ((count - expected_count) ** 2) / expected_count
            
            deviations[digit] = round(actual_pct - expected_pct, 2)
        
        is_suspicious = chi_square > 15.51
        
        return {
            "total_bids": total,
            "chi_square_statistic": round(chi_square, 4),
            "is_suspicious": is_suspicious,
            "significance_level": "0.05",
            "critical_value": 15.51,
            "actual_distribution": actual_percentages,
            "expected_distribution": benford_expected,
            "deviations": deviations,
            "interpretation": "Possible bid manipulation" if is_suspicious else "Distribution appears natural"
        }
    
    @staticmethod
    def detect_bid_clustering(bids: List[Dict], threshold_percent: float = 0.5) -> List[Dict]:
        
        clusters = []
        n = len(bids)
        
        for i in range(n):
            for j in range(i + 1, n):
                b1, b2 = bids[i], bids[j]
                diff = abs(b1["amount"] - b2["amount"])
                avg = (b1["amount"] + b2["amount"]) / 2
                percent_diff = (diff / avg) * 100 if avg > 0 else 0
                
                if percent_diff < threshold_percent:
                    clusters.append({
                        "bidder_1": b1["bidder_id"],
                        "bidder_2": b2["bidder_id"],
                        "amount_1": b1["amount"],
                        "amount_2": b2["amount"],
                        "difference": round(diff, 2),
                        "percent_difference": round(percent_diff, 4),
                        "severity": "HIGH" if percent_diff < 0.1 else "MEDIUM"
                    })
        
        clusters.sort(key=lambda x: (0 if x["severity"] == "HIGH" else 1, x["percent_difference"]))
        return clusters
    
    @staticmethod
    def calculate_collusion_risk(bidder_id: str, graph_signals: List[str], 
                                  stat_signals: List[str]) -> Dict:
        
        score = 0
        reasons = []
        
        if "shared_director" in graph_signals:
            score += 25
            reasons.append("Shared director with another bidder")
        if "shared_address" in graph_signals:
            score += 15
            reasons.append("Shared registered address")
        if "shared_bank" in graph_signals:
            score += 15
            reasons.append("Shared bank account")
        if "shared_phone" in graph_signals:
            score += 5
            reasons.append("Shared contact phone")
        
        if "bid_clustering" in stat_signals:
            score += 25
            reasons.append("Bid amount suspiciously close to competitor")
        if "benford_deviation" in stat_signals:
            score += 15
            reasons.append("Bid amounts deviate from expected statistical distribution")
        
        return {
            "bidder_id": bidder_id,
            "risk_score": min(score, 100),
            "risk_level": "CRITICAL" if score >= 80 else "HIGH" if score >= 60 else "MEDIUM" if score >= 40 else "LOW",
            "contributing_factors": reasons,
            "recommendation": "Immediate investigation" if score >= 80 else "Enhanced monitoring" if score >= 60 else "Standard review"
        }