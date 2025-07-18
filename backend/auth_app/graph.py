import random
from .models import Flight  # Replace 'your_app' with the actual app name where the Flight model is defined

def build_graph():
        DESTINATION_GRAPH = {}
        flights = Flight.objects.select_related('source', 'destination').all()
        for flight in flights:
            src = flight.source.name
            dest = flight.destination.name
            dist = random.randint(100, 1000)
            DESTINATION_GRAPH.setdefault(src, []).append((dest, dist))
            DESTINATION_GRAPH.setdefault(dest, []).append((src, dist))
        return DESTINATION_GRAPH