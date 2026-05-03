from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

class GraphBuilder:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    def close(self):
        self.driver.close()
    
    def seed_demo_data(self):
        with self.driver.session() as session:
            
            session.run("MATCH (n) DETACH DELETE n")
            
            
            session.run("""
                CREATE (b2:Bidder {id: 'B2', name: 'Beta Infra Ltd', bid_amount: 72400000, status: 'eligible'})
                CREATE (b5:Bidder {id: 'B5', name: 'Epsilon Corp', bid_amount: 72700000, status: 'eligible'})
                CREATE (dir:Director {id: 'DIR-001', name: 'Rajesh Kumar', pan: 'ABCPK1234R'})
                CREATE (addr:Address {id: 'ADDR-001', full: '42, Lajpat Nagar, New Delhi'})
                CREATE (bank:BankAccount {id: 'BANK-001', number: '****4521', ifsc: 'HDFC0001234'})
                CREATE (phone:Phone {id: 'PHONE-001', number: '+91-98765-43210'})
            """)
            
            
            session.run("""
                MATCH (b2:Bidder {id: 'B2'}), (b5:Bidder {id: 'B5'}), (dir:Director {id: 'DIR-001'}),
                      (addr:Address {id: 'ADDR-001'}), (bank:BankAccount {id: 'BANK-001'}), (phone:Phone {id: 'PHONE-001'})
                CREATE (dir)-[:DIRECTOR_OF]->(b2)
                CREATE (dir)-[:DIRECTOR_OF]->(b5)
                CREATE (b2)-[:REGISTERED_AT]->(addr)
                CREATE (b5)-[:REGISTERED_AT]->(addr)
                CREATE (b2)-[:USES_ACCOUNT]->(bank)
                CREATE (b5)-[:USES_ACCOUNT]->(bank)
                CREATE (b2)-[:CONTACT]->(phone)
                CREATE (b5)-[:CONTACT]->(phone)
            """)
            
            print(" Demo graph seeded")
    
    def detect_star_graphs(self):
        query = """
        MATCH (d:Director)-[:DIRECTOR_OF]->(b:Bidder)
        WITH d, count(b) as controlled_count, collect(b.name) as bidders
        WHERE controlled_count >= 2
        RETURN d.name as director, controlled_count, bidders
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [dict(record) for record in result]
    
    def detect_bid_clustering(self, threshold_percent=0.5):
        query = """
        MATCH (b1:Bidder), (b2:Bidder)
        WHERE b1.id < b2.id
        WITH b1, b2, abs(b1.bid_amount - b2.bid_amount) as diff,
             (b1.bid_amount + b2.bid_amount) / 2 as avg
        WITH b1, b2, diff, avg, (diff / avg) * 100 as percent_diff
        WHERE percent_diff < $threshold
        RETURN b1.name as bidder_1, b2.name as bidder_2,
               b1.bid_amount as amount_1, b2.bid_amount as amount_2,
               round(percent_diff, 4) as percent_difference
        """
        with self.driver.session() as session:
            result = session.run(query, threshold=threshold_percent)
            return [dict(record) for record in result]
    
    def get_full_network(self):
        with self.driver.session() as session:
            nodes = session.run("""
                MATCH (n) 
                RETURN labels(n)[0] as type, n.id as id, 
                       properties(n) as props
            """).data()
            
            edges = session.run("""
                MATCH (a)-[r]->(b)
                RETURN type(r) as type, a.id as source, b.id as target
            """).data()
            
            return {"nodes": nodes, "edges": edges}