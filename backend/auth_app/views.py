from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.middleware import csrf
from utils.firebase import verify_firebase_token
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from decimal import Decimal
import uuid

ROUTE_CACHE = {}
from .models import UserProfile, Admin, Booking, Destination, Flight, Hotel, Package, Payment
from firebase_admin import auth as firebase_auth
from .models import UserProfile
import random
import string
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from firebase_admin import auth as firebase_auth

from django.db.models import Q
from datetime import datetime
from django.db import models
from django.db import IntegrityError
import json


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from firebase_admin import auth as firebase_auth
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from firebase_admin import auth as firebase_auth
from .models import UserProfile, Booking
# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from firebase_admin import auth as firebase_auth
from django.core.mail import send_mail
from django.conf import settings
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from auth_app.models import UserProfile  # Ensure this matches your Django app name
import firebase_admin
from firebase_admin import auth
import random
import json
import requests  # ✅ Use requests for Firebase email/password login
from datetime import timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import firebase_admin.auth as firebase_auth
from django.conf import settings
from .models import TravelAgent 
FIREBASE_API_KEY = settings.FIREBASE_API_KEY 
def generate_temp_password(length=12):
    """Generates a secure temporary password."""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length)) # Ensure this is set in settings.py
import requests
import json
from django.http import JsonResponse
from collections import defaultdict
from .graph import build_graph 
from.get_all_paths import get_all_paths# Assuming these are defined in your graph module
DESTINATION_GRAPH = defaultdict(list)
 # 🔹 Replace with your Firebase Web API Key
 
def compute_package_availability(source, destination):
    import random
    from .models import Flight, Hotel

    


  

    

    def get_all_paths(graph, src, dest):
        paths = []

        def dfs(node, path, visited):
            if node == dest:
                paths.append(path[:])
                return
            for neighbor, _ in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, path, visited)
                    path.pop()
                    visited.remove(neighbor)

        dfs(src, [src], set([src]))
        return paths

    def compute_path_availability(path):
        print(f"\n🔍 Path: {' -> '.join(path)}")
        flight_avail = float('inf')
        hotel_avail = float('inf')
        hotel_found = False

        # 1. Check all flights in the path
        for i in range(len(path) - 1):
            src, dst = path[i], path[i + 1]
            flights = Flight.objects.filter(source__name=src, destination__name=dst)
            flight_seats = [f.available_seats for f in flights]
            print(f"✈️ Flights {src} → {dst}: {flight_seats}")
            if not flight_seats:
                print(f"❌ No flight between {src} and {dst}")
                return 0  # No flight = invalid path
            flight_avail = min(flight_avail, min(flight_seats))

        # 2. Check hotels only at source and destination (if available with >0 rooms)
        for stop in [path[0], path[-1]]:
            hotels = Hotel.objects.filter(destination__name=stop)
            rooms = [h.available_rooms for h in hotels if h.available_rooms > 0]
            print(f"🏨 Hotels at {stop} with rooms > 0: {rooms}")
            if rooms:
                hotel_found = True
                hotel_avail = min(hotel_avail, max(rooms))  # max per stop, min across stops

        # 3. Combine flight + hotel availability if hotels found
        if hotel_found:
            path_avail = min(flight_avail, hotel_avail)
            print(f"✅ Path availability: min(Flights={flight_avail}, Hotels={hotel_avail}) = {path_avail}")
        else:
            path_avail = flight_avail
            print(f"✅ Path availability (no valid hotels): {flight_avail}")
        return path_avail

    graph = build_graph()
    print(f"\n📌 Graph: {graph}")

    if source not in graph or destination not in graph:
        print(f"🚫 Either source '{source}' or destination '{destination}' not in graph.")
        return 0

    all_paths = get_all_paths(graph, source, destination)
    print(f"\n🛣️ All paths from {source} to {destination}:")
    for p in all_paths:
        print("   →", " -> ".join(p))

    if not all_paths:
        return 0

    all_availabilities = [compute_path_availability(p) for p in all_paths]
    print(f"\n📊 All path availabilities: {all_availabilities}")
    return max(all_availabilities)



@api_view(['GET'])
def searchpackagesuser(request):
    try:
        source_id = request.GET.get('source')
        destination_id = request.GET.get('destination')
        min_price = float(request.GET.get('min_price', 0))
        max_price = float(request.GET.get('max_price', 999999))

        if not source_id or not destination_id:
            return Response({'error': 'Source and destination IDs are required.'}, status=status.HTTP_400_BAD_REQUEST)

        packages = Package.objects.filter(
            source_id=source_id,
            destination_id=destination_id,
            price__gte=min_price,
            price__lte=max_price
        )

        available_packages = []
        for pkg in packages:
            availability = compute_package_availability(pkg.source.name, pkg.destination.name)
            if availability > 0:
                pkg_data = {
                    'id': pkg.id,
                    'name': pkg.name,
                    'source': pkg.source.name,
                    'destination': pkg.destination.name,
                    'price': float(pkg.price),
                    'discount': float(pkg.discount),
                    'duration_days': pkg.duration_days,
                    'image_url': pkg.image_url,
                    'availability': availability,
                    'reviews': []
                }

                # Fetch reviews
                content_type = ContentType.objects.get_for_model(Package)
                reviews = Review.objects.filter(content_type=content_type, object_id=pkg.id)
                pkg_data['reviews'] = [
                    {
                        'user_id': r.user.id,
                        'rating': r.rating,
                        'feedback': r.feedback
                    }
                    for r in reviews
                ]

                available_packages.append(pkg_data)

        return Response(available_packages, status=status.HTTP_200_OK)

    except Exception as e:
        print("❌ Package search error:", str(e))
        return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def exchange_refresh_token(refresh_token):
    """ Exchanges a refresh token for a new ID token using Firebase API """
    url = f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_API_KEY}"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    try:
        response = requests.post(url, data=payload)
        data = response.json()

        if "id_token" in data:
            return data["id_token"]  # ✅ Return the new ID token

        print("Error exchanging refresh token:", data)
        return None
    except Exception as e:
        print("Request error:", str(e))
        return None

def get_user_role_from_refresh_token(request):
    try:
        # 🔹 Get the refresh token from cookies or headers
        refresh_token = request.COOKIES.get('refresh_token') or request.headers.get('X-Refresh-Token')

        if not refresh_token:
            print("No refresh token found in cookies or headers")
            return None

        # 🔹 Exchange refresh token for a new ID token
        id_token = exchange_refresh_token(refresh_token)

        if not id_token:
            print("Failed to get ID token from refresh token")
            return None

        # 🔹 Verify the new ID token
        decoded_token = firebase_auth.verify_id_token(id_token, clock_skew_seconds=10)
        uid = decoded_token.get('uid')

        # 🔹 Fetch role from Firebase custom claims
        firebase_user = auth.get_user(uid)  
        user_claims = firebase_user.custom_claims or {}  

        role = user_claims.get('role', 'client')  # Default to client if role is missing

        print(f"User Role: {role}")  # ✅ Debugging: Print role in logs
        return role

    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        return None
@csrf_exempt
@require_http_methods(["PATCH"])
def update_flight_availability(request, flight_id):
    try:
        flight = Flight.objects.get(id=flight_id)
    except Flight.DoesNotExist:
        return JsonResponse({'error': 'Flight not found'}, status=404)

    try:
        data = json.loads(request.body.decode('utf-8'))

        if 'is_available' in data:
            flight.is_available = data['is_available']

        if 'available_seats' in data:
            flight.available_seats = data['available_seats']

        flight.save()

        return JsonResponse({
            'message': 'Flight updated successfully.',
            'flight_id': flight_id,
            'flight_number': flight.flight_number,
            'updated_fields': {
                'is_available': flight.is_available,
                'available_seats': flight.available_seats
            }
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
@csrf_exempt
def add_package(request):
    """Admin API to add a new travel package."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    try:
        data = json.loads(request.body)

        name = data.get('name', '').strip()
        source_id = data.get('source')
        destination_id = data.get('destination')
        duration_days = data.get('duration_days')
        price = data.get('price')
        discount = data.get('discount', 0)
        image_url = data.get('image_url', '').strip()

        # ✅ Validate required fields
        print(f"Received data: {data}")
        if not name or not source_id or not destination_id or not price or not duration_days:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        if source_id == destination_id:
            return JsonResponse({'error': 'Source and destination cannot be the same'}, status=400)

        # ✅ Fetch destination objects
        source = Destination.objects.get(id=source_id)
        destination = Destination.objects.get(id=destination_id)

        # ✅ Create and validate package
        package = Package(
            name=name,
            source=source,
            destination=destination,
            price=price,
            duration_days=duration_days,
            discount=discount,
            image_url=image_url
        )

        package.clean()
        package.save()

        return JsonResponse({
            'message': 'Package created successfully',
            'package': {
                'id': package.id,
                'name': package.name,
                'source': package.source.name,
                'destination': package.destination.name,
                'price': str(package.price),
                'discount': str(package.discount),
                'duration_days': package.duration_days,
                'image_url': package.image_url
            }
        }, status=201)

    except Destination.DoesNotExist:
        return JsonResponse({'error': 'Invalid source or destination ID'}, status=400)

    except ValidationError as ve:
        return JsonResponse({'error': str(ve)}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Flight

@api_view(['GET'])
def search_flights(request):
    source = request.GET.get('source')
    destination = request.GET.get('destination')
    flight_number = request.GET.get('flight_number')
    is_available = request.GET.get('is_available')  # should be 'true' or 'false'

    flights = Flight.objects.all()

    if source:
        if source.isdigit():
            flights = flights.filter(source__id=int(source))
        else:
            flights = flights.filter(source__name__icontains=source)

    if destination:
        if destination.isdigit():
            flights = flights.filter(destination__id=int(destination))
        else:
            flights = flights.filter(destination__name__icontains=destination)

    if flight_number:
        flights = flights.filter(flight_number__icontains=flight_number)

    if is_available is not None:
        if is_available.lower() == 'true':
            flights = flights.filter(is_available=True)
        elif is_available.lower() == 'false':
            flights = flights.filter(is_available=False)

    data = [
        {
            "id": flight.id,
            "flight_number": flight.flight_number,
            "source": flight.source.name,
            "destination": flight.destination.name,
            "available_seats": flight.available_seats,
            "price_per_seat": float(flight.price_per_seat),
            "discount": float(flight.discount),
            "is_available": flight.is_available,
        }
        for flight in flights
    ]
    return Response(data)

@require_GET
def search_destinations(request):
    query = request.GET.get('q', '')
    destinations = Destination.objects.filter(name__icontains=query, availability=True)

    response_data = [
        {
            'id': dest.id,
            'name': dest.name,
            'location': dest.location,
            'image_url': dest.image_url,
            'price': str(dest.price)
        }
        for dest in destinations
    ]

    return JsonResponse(response_data, safe=False)
@api_view(['PATCH'])
def update_flight(request, flight_id):
    try:
        flight = Flight.objects.get(id=flight_id)
    except Flight.DoesNotExist:
        return Response({'error': 'Flight not found'}, status=404)

    response_data = {
        "flight_id": flight.id,
    }

    # Flight number
    new_number = request.data.get('flight_number')
    if new_number and new_number != flight.flight_number:
        response_data['previous_flight_number'] = flight.flight_number
        response_data['updated_flight_number'] = new_number
        flight.flight_number = new_number

    # Source (using ID)
    source_id = request.data.get('source_id')
    if source_id:
        try:
            
            new_source = Destination.objects.get(id=int(source_id))
            if new_source != flight.source:
                response_data['previous_source'] = flight.source.name
                response_data['updated_source'] = new_source.name
                flight.source = new_source
        except Destination.DoesNotExist:
            return Response({'error': 'Invalid source ID'}, status=400)

    # Destination (using ID)
    destination_id = request.data.get('destination_id')
    if destination_id:
        try:
            new_dest = Destination.objects.get(id=int(destination_id))
            if new_dest != flight.destination:
                response_data['previous_destination'] = flight.destination.name
                response_data['updated_destination'] = new_dest.name
                flight.destination = new_dest
        except Destination.DoesNotExist:
            return Response({'error': 'Invalid destination ID'}, status=400)

    # Discount
    new_discount = request.data.get('discount')
    if new_discount is not None and new_discount != flight.discount:
        response_data['previous_discount'] = flight.discount
        response_data['updated_discount'] = new_discount
        flight.discount = new_discount

    # Price
    new_price = request.data.get('price_per_seat')
    if new_price is not None and new_price != flight.price_per_seat:
        response_data['previous_price'] = flight.price_per_seat
        response_data['updated_price'] = new_price
        flight.price_per_seat = new_price

    flight.save()
    return Response(response_data)

@api_view(['PATCH'])
def update_hotel(request, hotel_id):
    try:
        hotel = Hotel.objects.get(id=hotel_id)
    except Hotel.DoesNotExist:
        return Response({'error': 'Hotel not found'}, status=status.HTTP_404_NOT_FOUND)

    updated_fields = {}

    if 'available_rooms' in request.data:
        hotel.available_rooms = request.data['available_rooms']
        updated_fields['available_rooms'] = hotel.available_rooms

    if 'is_available' in request.data:
        hotel.is_available = request.data['is_available']
        updated_fields['is_available'] = hotel.is_available

    if 'price_per_night' in request.data:
        hotel.price_per_night = request.data['price_per_night']
        updated_fields['price_per_night'] = hotel.price_per_night

    if 'discount' in request.data:
        hotel.discount = request.data['discount']
        updated_fields['discount'] = hotel.discount

    hotel.save()

    return Response({
        'message': 'Hotel updated successfully',
        'hotel_id': hotel.id,
        'updated_fields': updated_fields
    }, status=status.HTTP_200_OK)
@api_view(['PATCH'])
def update_package(request, package_id):
    try:
        package = Package.objects.get(id=package_id)
    except Package.DoesNotExist:
        return Response({'error': 'Package not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    updated_fields = {}

    # Compare and update source
    new_source_id = data.get('source')
    if new_source_id and new_source_id != package.source.id:
        try:
            new_source = Destination.objects.get(id=new_source_id)
        except Destination.DoesNotExist:
            return Response({'error': 'Invalid source ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        updated_fields['source'] = {
            'previous': package.source.name,
            'current': new_source.name
        }
        package.source = new_source

    # Compare and update price
    if 'price' in data and str(package.price) != str(data['price']):
        updated_fields['price'] = data['price']
        package.price = data['price']

    # Compare and update discount
    if 'discount' in data and str(package.discount) != str(data['discount']):
        updated_fields['discount'] = data['discount']
        package.discount = data['discount']

    # Compare and update duration
    if 'duration_days' in data and package.duration_days != data['duration_days']:
        updated_fields['duration_days'] = data['duration_days']
        package.duration_days = data['duration_days']

    if not updated_fields:
        return Response({'message': 'No changes detected'}, status=status.HTTP_200_OK)

    package.save()

    return Response({
        'message': 'Package updated successfully',
        'package_id': package.id,
        'updated_fields': updated_fields
    }, status=status.HTTP_200_OK)
@api_view(['GET'])
def search_hotels(request):
    query = request.GET.get('query', '')
    is_available = request.GET.get('is_available')

    hotels = Hotel.objects.select_related('destination').all()

    if query:
        hotels = hotels.filter(
            Q(name__icontains=query) |
            Q(destination__name__icontains=query)
        )

    if is_available is not None:
        if is_available.lower() == 'true':
            hotels = hotels.filter(is_available=True)
        elif is_available.lower() == 'false':
            hotels = hotels.filter(is_available=False)

    # Custom output to include destination name and is_available explicitly
    result = [
        {
            "id": h.id,
            "name": h.name,
            "destination": h.destination.name,
            "is_available": h.is_available,
            "available_rooms": h.available_rooms,
            "discount": str(h.discount),
            "image_url": h.image_url,
            "price_per_night": str(h.price_per_night),
            "created_at": h.created_at,
            "updated_at": h.updated_at,
        }
        for h in hotels
    ]

    return JsonResponse(result, safe=False)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Hotel, Review

from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.db.models import Q
from rest_framework.decorators import api_view
from .models import Hotel, Review
from django.db.models import Avg
@api_view(['POST'])
def add_or_update_review(request):
    try:
        user_id = request.data.get('user_id')
        object_id = request.data.get('object_id')
        model_name = request.data.get('model_name')  # 'hotel', 'flight', or 'package'
        rating = request.data.get('rating')
        feedback = request.data.get('feedback', '')

        # Validate required fields
        if not all([user_id, object_id, model_name, rating]):
            return JsonResponse({'error': 'user_id, object_id, model_name, and rating are required.'}, status=400)

        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                return JsonResponse({'error': 'Rating must be between 1 and 5.'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Rating must be an integer.'}, status=400)

        # Get user profile
        try:
            user_profile = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)

        # Get content type for generic relation
        try:
            content_type = ContentType.objects.get(model=model_name.lower())
        except ContentType.DoesNotExist:
            return JsonResponse({'error': 'Invalid model name.'}, status=400)

        # Check if review already exists
        review, created = Review.objects.update_or_create(
            user=user_profile,
            content_type=content_type,
            object_id=object_id,
            defaults={'rating': rating, 'feedback': feedback}
        )

        return JsonResponse({
            'success': True,
            'message': 'Review created.' if created else 'Review updated.',
            'review': {
                'user': user_profile.display_name,
                'rating': review.rating,
                'feedback': review.feedback,
                'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@api_view(['GET'])
def filter_hotels_advanced(request):
    destination = request.GET.get('destination')
    guests = request.GET.get('guests')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if not all([destination, guests, min_price, max_price]):
        return Response({'error': 'All filters (destination, guests, min_price, max_price) are required.'}, status=400)

    try:
        guests = int(guests)
        min_price = float(min_price)
        max_price = float(max_price)
    except ValueError:
        return Response({'error': 'Invalid number format for guests or price range.'}, status=400)

    hotel_qs = Hotel.objects.select_related('destination').filter(
        destination__name__icontains=destination,
        available_rooms__gte=guests,
        price_per_night__gte=min_price,
        price_per_night__lte=max_price,
        is_available=True
    )

    hotel_content_type = ContentType.objects.get_for_model(Hotel)

    # Create paginated response
    paginator = HotelPagination()
    page = paginator.paginate_queryset(hotel_qs, request)

    results = []
    for hotel in page:
        reviews = Review.objects.filter(
            content_type=hotel_content_type,
            object_id=hotel.id
        )
        reviews_data = [
            {
                "user": review.user.display_name,
                "rating": review.rating,
                "comment": review.feedback,
                "created_at": review.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for review in reviews
        ]
        avg_rating = reviews.aggregate(average=Avg('rating'))['average'] or 0.0

        results.append({
            "id": hotel.id,
            "name": hotel.name,
            "destination": hotel.destination.name,
            "available_rooms": hotel.available_rooms,
            "price_per_night": str(hotel.price_per_night),
            "discount": str(hotel.discount),
            "is_available": hotel.is_available,
            "image_url": hotel.image_url,
            "average_rating": round(avg_rating, 1),
            "reviews": reviews_data
        })

    return paginator.get_paginated_response(results)

@api_view(['GET'])
def view_package_details(request, package_id):
    print(f"Fetching package details for ID: {package_id}")
    package = get_object_or_404(Package, id=package_id)
    source = package.source.name
    destination = package.destination.name
    print(f"Source: {source}, Destination: {destination}")

    graph = build_graph()
    print("Graph built:", graph)

    all_paths = get_all_paths(graph, source, destination)
    print(f"All paths from {source} to {destination}: {all_paths}")

    valid_paths = []

    def compute_path_info(path):
        print(f"\nEvaluating path: {path}")
        path_flights = []
        flight_avail = float('inf')
        hotel_avail = float('inf')
        hotel_found = False

        source_hotels = []
        destination_hotels = []
        intermediate_hotels = {}
        hotel_prices = []

        # Step 1: Flights
        for i in range(len(path) - 1):
            src, dst = path[i], path[i + 1]
            flights = Flight.objects.filter(source__name=src, destination__name=dst)
            print(f"Flights from {src} to {dst}: {[f.flight_number for f in flights]}")

            flight_data = []
            for f in flights:
                if f.available_seats is None or f.available_seats <= 0:
                    print(f"Skipping flight {f.flight_number} due to unavailable seats ({f.available_seats})")
                    continue
                flight_info = {
                    'id': f.id,
                    'flight_number': f.flight_number,
                    'departure': f.source.name,
                    'arrival': f.destination.name,
                    'available_seats': f.available_seats,
                    'price_per_seat': float(f.price_per_seat),
                    'discount': float(f.discount),
                    'icon_url': f.flight_icon_url
                }
                flight_data.append(flight_info)

            if not flight_data:
                print(f"No valid flights from {src} to {dst}, skipping path.")
                return None

            path_flights.extend(flight_data)
            flight_avail = min(flight_avail, min(f['available_seats'] for f in flight_data))

        # Step 2: Hotels (source, destination, and intermediate)
        for idx, stop in enumerate(path):
            hotels = Hotel.objects.filter(destination__name=stop)
            print(f"\nRaw hotel data at {stop}:")
            hotel_data = []
            stop_hotels = []

            for h in hotels:
                print(f" - {h.name} | Available Rooms: {h.available_rooms}")
                if h.available_rooms and h.available_rooms > 0:
                    hotel_data.append({
                        'id': h.id,
                        'name': h.name,
                        'available_rooms': h.available_rooms,
                        'price_per_night': float(h.price_per_night)
                    })
                    stop_hotels.append({
                        'id': h.id,
                        'name': h.name,
                        'available_rooms': h.available_rooms,
                        'price_per_night': float(h.price_per_night)
                    })

            if hotel_data:
                hotel_found = True
                stop_min_rooms = min(h['available_rooms'] for h in hotel_data)
                hotel_avail = min(hotel_avail, stop_min_rooms)

                # Pick cheapest hotel for price calculation
                cheapest = min(stop_hotels, key=lambda h: h['price_per_night'])
                hotel_prices.append(cheapest['price_per_night'])

                if idx == 0:
                    source_hotels = hotel_data
                elif idx == len(path) - 1:
                    destination_hotels = hotel_data
                else:
                    intermediate_hotels[stop] = hotel_data

        # Step 3: Final Availability
        availability = min(flight_avail, hotel_avail) if hotel_found else flight_avail
        print(f"\n✅ Calculated availability for path {path}: {availability}")

        if availability <= 0:
            print("❌ Availability is 0, skipping this path.")
            return None

        # Step 4: Price Calculation
        total_flight_price = sum(
            f['price_per_seat'] * (1 - f['discount'] / 100) for f in path_flights
        )

        total_hotel_price = sum(hotel_prices) * (package.duration_days * 2)  # 2 nights per day
        package_base_price = float(package.price) * (1 - float(package.discount) / 100)

        final_price = round(package_base_price + total_flight_price + total_hotel_price, 2)
        print(f"💰 Final price for path {path}: {final_price}")

        return {
            'path': path,
            'flights': path_flights,
            'availability': availability,
            'source_hotels': source_hotels,
            'intermediate_hotels': intermediate_hotels,
            'destination_hotels': destination_hotels,
            'price': final_price
        }

    # Final loop
    for path in all_paths:
        info = compute_path_info(path)
        if info:
            valid_paths.append(info)
            print("✔️ Valid path added.")
        else:
            print("❌ Invalid or unavailable path skipped.")

    print(f"\n🎯 Total valid paths found: {len(valid_paths)}")

    return JsonResponse({
        'package': {
            'id': package.id,
            'name': package.name,
            'source': source,
            'destination': destination,
            'price': float(package.price),
            'duration_days': package.duration_days,
            'discount': float(package.discount),
            'image_url': package.image_url,
        },
        'valid_paths': valid_paths
    }, safe=False)


# Packages search
@api_view(['GET'])
def search_packages(request):
    query = request.GET.get('query', '')
    is_available = request.GET.get('is_available')

    packages = Package.objects.all()

    if query:
        packages = packages.filter(
            Q(name__icontains=query) |
            Q(source__name__icontains=query) |
            Q(destination__name__icontains=query)
        )

    if is_available is not None:
        if is_available.lower() == 'true':
            packages = packages.filter(is_available=True)
        elif is_available.lower() == 'false':
            packages = packages.filter(is_available=False)

    # 👇 This must come before looping
    data = packages.values(
        'id',
        'name',
        'discount',
        'price',
        'duration_days',
        'image_url',
        'is_available',
        'created_at',
        'updated_at',
        'source_id',
        'source__name',
        'destination_id',
        'destination__name'
    )

    results = []
    for item in data:
        # ✅ Compute dynamic availability
        availability = compute_package_availability(
            item['source__name'], item['destination__name']
        )

        results.append({
            'id': item['id'],
            'name': item['name'],
            'discount': item['discount'],
            'image_url': item['image_url'],
            'is_available': item['is_available'],
            'availability': availability,  # 👈 included here
            'price': item['price'],
            'duration_days': item['duration_days'],
            'created_at': item['created_at'],
            'updated_at': item['updated_at'],
            'source': {
                'id': item['source_id'],
                'name': item['source__name']
            },
            'destination': {
                'id': item['destination_id'],
                'name': item['destination__name']
            }
        })

    return JsonResponse(results, safe=False)
@csrf_exempt
def add_hotel(request):
    """Admin can add a new hotel."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    try:
        data = json.loads(request.body)

        name = data.get('name', '').strip()
        destination_id = data.get('destination')
        available_rooms = data.get('available_rooms')
        discount = data.get('discount', 0)
        image_url = data.get('image_url', '').strip()
        price_per_night = data.get('price_per_night')

        # ✅ Validate required fields
        if not name or not destination_id or available_rooms is None or price_per_night is None:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        # ✅ Fetch destination
        try:
            destination = Destination.objects.get(id=destination_id)
        except Destination.DoesNotExist:
            return JsonResponse({'error': 'Invalid destination ID'}, status=400)

        # ✅ Create hotel
        hotel = Hotel.objects.create(
            name=name,
            destination=destination,
            available_rooms=available_rooms,
            discount=discount,
            price_per_night=price_per_night,
            image_url=image_url
        )

        return JsonResponse({
            'message': 'Hotel added successfully',
            'hotel': {
                'id': hotel.id,
                'name': hotel.name,
                'destination': hotel.destination.name,
                'available_rooms': hotel.available_rooms,
                'discount': str(hotel.discount),
                'price_per_night': str(hotel.price_per_night),
                'image_url': hotel.image_url
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_all_destinations(request):
    destinations = Destination.objects.all().values('id', 'name')
    return JsonResponse({'destinations': list(destinations)}, status=200)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Destination, DestinationConnection
import json, random

@csrf_exempt
def add_destination(request):
    """Admin can add new destinations with random graph connections."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    try:
        # ✅ Parse request body
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        location = data.get('location', '').strip()
        image_url = data.get('image_url', '').strip()
        price = data.get('price')
        availability = data.get('availability', True)

        # ✅ Validate required fields
        if not name or not location or not price:
            return JsonResponse({'error': 'Name, location, and price are required'}, status=400)

        # ✅ Check for duplicate destination
        if Destination.objects.filter(name=name).exists():
            return JsonResponse({'error': 'Destination already exists'}, status=400)

        # ✅ Create Destination
        destination = Destination.objects.create(
            name=name,
            description=description,
            location=location,
            image_url=image_url,
            price=price,
            availability=availability
        )

        # ✅ Randomly connect to up to 2 existing destinations
        existing_destinations = list(Destination.objects.exclude(id=destination.id))
        connected_to = []

        if existing_destinations:
            connections = random.sample(existing_destinations, min(2, len(existing_destinations)))
            for conn_dest in connections:
                distance = random.randint(100, 1000)

                # Add both directions
                DestinationConnection.objects.create(source=destination, destination=conn_dest, distance=distance)
                DestinationConnection.objects.create(source=conn_dest, destination=destination, distance=distance)

                connected_to.append({
                    'destination': conn_dest.name,
                    'distance_km': distance
                })

        return JsonResponse({
            'message': 'Destination added successfully',
            'destination': {
                'id': destination.id,
                'name': destination.name,
                'location': destination.location,
                'price': str(destination.price),
                'availability': destination.availability,
                'connected_to': connected_to
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict, deque
import heapq

from collections import defaultdict, deque
import heapq

import heapq
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Flight
  # Adjust import to your app name

@csrf_exempt
def logout_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

    try:
        session_cookie = request.COOKIES.get('session')

        if not session_cookie:
            return JsonResponse({'error': 'Session cookie not found'}, status=400)

        # ✅ Verify session cookie to get UID
        decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
        uid = decoded_claims['uid']

        # ✅ Revoke Firebase session (optional)
        auth.revoke_refresh_tokens(uid)

        # ✅ Create response with cleared cookies
        res = JsonResponse({'message': 'Logout successful'})
        res.delete_cookie('session')
        res.delete_cookie('refresh_token')

        return res

    except auth.InvalidSessionCookieError:
        return JsonResponse({'error': 'Invalid session cookie'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
def get_flight_routes(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET requests allowed'}, status=405)

    try:
        # ✅ Check for route ID early
        route_id = request.GET.get('id')
        if route_id:
            route = ROUTE_CACHE.get(route_id)
            if route:
                return JsonResponse(route, status=200)
            else:
                return JsonResponse({'error': 'Route not found'}, status=404)

        # ✅ Fallback to source-destination logic
        source = request.GET.get('source')
        destination = request.GET.get('destination')

        if not source or not destination:
            return JsonResponse({'error': 'Both source and destination are required'}, status=400)

        DESTINATION_GRAPH.clear()
        flights = Flight.objects.select_related('source', 'destination').all()

        for flight in flights:
            src = flight.source.name
            dest = flight.destination.name
            distance = random.randint(100, 1000)  # Simulated distance

            DESTINATION_GRAPH.setdefault(src, [])
            DESTINATION_GRAPH.setdefault(dest, [])

            if all(neigh != dest for neigh, _ in DESTINATION_GRAPH[src]):
                DESTINATION_GRAPH[src].append((dest, distance))
            if all(neigh != src for neigh, _ in DESTINATION_GRAPH[dest]):
                DESTINATION_GRAPH[dest].append((src, distance))

        if source not in DESTINATION_GRAPH or destination not in DESTINATION_GRAPH:
            return JsonResponse({
                'source': source,
                'destination': destination,
                'all_paths': [],
                'shortest_path': {}
            }, status=200)

        # DFS to find all paths
        all_paths = []

        def dfs(curr, end, visited, path, distance):
            if curr == end:
                all_paths.append((path[:], distance))
                return
            for neighbor, dist in DESTINATION_GRAPH.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, end, visited, path, distance + dist)
                    visited.remove(neighbor)
                    path.pop()

        dfs(source, destination, set([source]), [source], 0)

        # Dijkstra for shortest path
        def dijkstra(src, dest):
            pq = [(0, src, [src])]
            visited = set()

            while pq:
                cost, node, path = heapq.heappop(pq)
                if node == dest:
                    return cost, path
                if node in visited:
                    continue
                visited.add(node)
                for neighbor, dist in DESTINATION_GRAPH.get(node, []):
                    if neighbor not in visited:
                        heapq.heappush(pq, (cost + dist, neighbor, path + [neighbor]))
            return float('inf'), []

        shortest_distance, shortest_path = dijkstra(source, destination)

        path_details = []

        for path, dist in all_paths:
            valid = True
            legs = []
            all_available_seats = []

            for i in range(len(path) - 1):
                flights_between = Flight.objects.filter(
                    source__name=path[i],
                    destination__name=path[i + 1]
                ).values('id', 'flight_number', 'available_seats', 'price_per_seat')

                if not flights_between.exists():
                    valid = False
                    break

                segment_distance = next((d for a, d in DESTINATION_GRAPH[path[i]] if a == path[i + 1]), 0)
                time_hours = segment_distance / 300

                flights_list = list(flights_between)
                if flights_list:
                    all_available_seats.append(min(f['available_seats'] for f in flights_list))

                legs.append({
                    'from': path[i],
                    'to': path[i + 1],
                    'flights': flights_list,
                    'time_hours': round(time_hours, 2)
                })

            if valid:
                min_seats = min(all_available_seats) if all_available_seats else 0
                if min_seats > 0:
                    route_obj = {
            'route_id': str(uuid.uuid4()),
            'route': path,
            'total_distance': dist,
            'total_time_hours': round(dist / 300, 2),
            'legs': legs,
             'min_available_seats': min_seats
                               }

        ROUTE_CACHE[route_obj['route_id']] = route_obj
        path_details.append(route_obj)


        return JsonResponse({
            'source': source,
            'destination': destination,
            'all_paths': path_details,
            'shortest_path': {
                'route': shortest_path,
                'total_distance': shortest_distance,
                'total_time_hours': round(shortest_distance / 300, 2)
            } if shortest_path else {}
        }, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
import json
from .models import Booking, Destination, Flight, UserProfile
@csrf_exempt
def book_package_path(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

    try:
        data = json.loads(request.body)

        user_id = data.get('user_id')  # 🔁 or use request.user.id if logged in
        package_id = data.get('package_id')
        number_of_people = data.get('number_of_people')
        status = data.get('status', 'pending')  # default to pending
        flight_ids = data.get('flights', [])
        hotel_ids = data.get('hotels', [])

        if not all([user_id, package_id, number_of_people]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        user = UserProfile.objects.get(id=user_id)
        package = Package.objects.get(id=package_id)

        flights = Flight.objects.filter(id__in=flight_ids)
        hotels = Hotel.objects.filter(id__in=hotel_ids)

        # ✅ Total price = base package + selected flights + optional hotels
        total_price = package.price
        for flight in flights:
            total_price += flight.price_per_seat * Decimal(number_of_people)

        for hotel in hotels:
            total_price += hotel.price_per_night * Decimal(number_of_people)  # or adjust logic

        # ✅ Create the Booking entry
        booking = Booking.objects.create(
            user=user,
            source=package.source,
            destination=package.destination,
            number_of_people=number_of_people,
            total_price=total_price,
            status=status,
            category='package',
            packages=package  # Link to the package
        )

        # ✅ Add flights/hotels to package (optional: clone package if needed)
        package.flights.set(flights)
        package.hotels.set(hotels)

        return JsonResponse({
            'message': 'Booking created successfully.',
            'booking_id': booking.id,
            'total_price': float(total_price),
            'status': booking.status
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
def create_flight_booking(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

    try:
        data = json.loads(request.body)

        user_id = data.get('user_id')
        source_id = data.get('source_id')
        destination_id = data.get('destination_id')
        number_of_people = data.get('number_of_people')
        flight_numbers = data.get('flight_numbers')

        if not all([user_id, source_id, destination_id, number_of_people, flight_numbers]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        user = UserProfile.objects.get(id=user_id)
        source = Destination.objects.get(id=source_id)
        destination = Destination.objects.get(id=destination_id)

        total_price = 0
        flights = []

        for fn in flight_numbers:
            flight = Flight.objects.get(flight_number=fn)

            # ✅ Just check availability (don't deduct yet)
            if flight.available_seats < number_of_people:
                return JsonResponse({'error': f'Not enough seats for flight {fn}'}, status=400)

            price = flight.price_per_seat
            if flight.discount:
                price = price * (1 - flight.discount / 100)
            total_price += price * number_of_people
            flights.append(flight)

        booking = Booking.objects.create(
            user=user,
            source=source,
            destination=destination,
            number_of_people=number_of_people,
            total_price=total_price,
            status='pending',  # ✅ Seats will be deducted later upon payment
            category='flight'
        )

        for flight in flights:
            booking.flights.add(flight)

        booking.save()

        flight_data = []
        for flight in booking.flights.all():
            flight_data.append({
                'flight_number': flight.flight_number,
                'source': flight.source.name,
                'destination': flight.destination.name,
            })

        response_data = {
            'booking_id': booking.id,
            'user_id': user.id,
            'source_id': source.id,
            'source_name': source.name,
            'destination_id': destination.id,
            'destination_name': destination.name,
            'number_of_people': booking.number_of_people,
            'total_price': float(booking.total_price),
            'status': booking.status,
            'category': booking.category,
            'flights': flight_data
        }

        return JsonResponse(response_data, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@api_view(['POST'])
def confirmflight(request):
    try:
        booking_id = request.data.get('booking_id')
        payment_method = request.data.get('payment_method')

        if not booking_id:
            return Response({'error': 'Booking ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(booking, 'payment') and booking.payment.status == 'completed':
            return Response({'message': 'Payment already completed.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total amount from flights
        total_amount = 0
        for flight in booking.flights.all():
            if flight.available_seats < booking.number_of_people:
                return Response({'error': f'Not enough seats on flight {flight.flight_number}.'}, status=status.HTTP_400_BAD_REQUEST)
            total_amount += float(flight.price_per_seat) * booking.number_of_people

        # Generate transaction ID
        transaction_id = str(uuid.uuid4())

        # Create or update payment
        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': total_amount,
                'status': 'completed',
                'transaction_id': transaction_id
            }
        )

        if not created:
            payment.status = 'completed'
            payment.amount = total_amount
            payment.transaction_id = transaction_id
            payment.save()

        # Update booking status
        booking.status = 'confirmed'
        booking.save()

        # Deduct seats
        for flight in booking.flights.all():
            flight.available_seats -= booking.number_of_people
            flight.save()

        return Response({
            'message': 'Payment successful and booking confirmed.',
            'transaction_id': transaction_id
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print("❌ Payment error:", str(e))

        # Set payment status to failed if booking exists
        booking_id = request.data.get('booking_id')
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                if hasattr(booking, 'payment'):
                    booking.payment.status = 'failed'
                    booking.payment.save()
            except Exception as inner_error:
                print("⚠️ Failed to mark payment as failed:", inner_error)

        return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def confirmhotel(request):
    try:
        booking_id = request.data.get('booking_id')
        payment_method = request.data.get('payment_method')

        if not booking_id:
            return Response({'error': 'Booking ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.select_related('hotels', 'user', 'payment').get(id=booking_id, category='hotel')
        except Booking.DoesNotExist:
            return Response({'error': 'Hotel booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        print("📦 Booking ID:", booking.id)
        print("🏨 Hotel:", booking.hotels)

        hotel = booking.hotels  # use the correct field name

        if not hotel:
            return Response({'error': 'Associated hotel not found in booking.'}, status=status.HTTP_400_BAD_REQUEST)

        if hasattr(booking, 'payment') and booking.payment.status == 'completed':
            return Response({'message': 'Payment already completed.'}, status=status.HTTP_400_BAD_REQUEST)

        total_amount = float(booking.total_price)
        transaction_id = str(uuid.uuid4())

        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': total_amount,
                'status': 'completed',
                'transaction_id': transaction_id
            }
        )

        if not created:
            payment.status = 'completed'
            payment.amount = total_amount
            payment.transaction_id = transaction_id
            payment.save()

        # Deduct rooms
        print(f"🛏 Rooms before: {hotel.available_rooms}")
        rooms_to_deduct = getattr(booking, 'num_rooms_booked', 1)  # default to 1 if not set
        hotel.available_rooms = max(hotel.available_rooms - rooms_to_deduct, 0)
        hotel.save()
        print(f"🛏 Rooms after: {hotel.available_rooms}")

        booking.status = 'confirmed'
        booking.save()

        return Response({
            'message': 'Hotel booking confirmed and payment completed.',
            'transaction_id': transaction_id
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print("❌ Hotel Payment Error:", str(e))
        return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from django.db import IntegrityError

@api_view(['POST'])
def confirm_package(request):
    booking_id = request.data.get('booking_id')
    transaction_id = request.data.get('transaction_id')
    new_status = request.data.get('status')  # completed / failed / pending

    if not all([booking_id, new_status]):
        return Response({'error': 'booking_id and status are required.'}, status=status.HTTP_400_BAD_REQUEST)

    booking = get_object_or_404(Booking, id=booking_id)

    # ✅ Get linked package
    package = booking.packages
    if not package:
        return Response({'error': 'No package linked to this booking.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # ✅ Only create payment if not already exists
        if hasattr(booking, 'payment'):
            payment = booking.payment
        else:
            payment = Payment(booking=booking)

        payment.status = new_status
        payment.amount = booking.total_price
        if transaction_id:
            payment.transaction_id = transaction_id
        payment.save()

        if new_status == 'completed':
            booking.status = 'confirmed'
            booking.save()

            for flight in package.flights.all():
                flight.available_seats = max(0, flight.available_seats - booking.number_of_people)
                flight.save()

            for hotel in package.hotels.all():
                hotel.available_rooms = max(0, hotel.available_rooms - booking.number_of_people)
                hotel.save()

        return Response({'message': 'Payment updated and availability adjusted successfully.'}, status=status.HTTP_200_OK)

    except IntegrityError as e:
        return Response({'error': f'IntegrityError: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from django.http import JsonResponse
from .models import Booking

def get_booking_history(request, user_id):
    try:
        user = UserProfile.objects.get(id=user_id)
        bookings = Booking.objects.filter(user=user, status__in=['confirmed', 'cancelled'])

        data = []
        for booking in bookings:
            item = {
                'booking_id': booking.id,
                'user_id': booking.user.id,
                'category': booking.category,
                'status': booking.status,
                'total_price': booking.total_price,
                'number_of_people': booking.number_of_people,
                'booking_date': booking.booking_date.strftime("%Y-%m-%d %H:%M:%S"),
                'source': booking.source.name,
                'destination': booking.destination.name
            }

            if booking.category == 'hotel' and booking.hotels:
                item['hotel'] = {'id': booking.hotels.id}
            elif booking.category == 'flight' and booking.flights:
                item['flight'] = {'id': booking.flights.id}
            elif booking.category == 'package' and booking.packages:
                item['package'] = {'id': booking.packages.id}

            data.append(item)

        return JsonResponse({'bookings': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['POST'])
def process_refund(request, booking_id):
  

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found.'}, status=404)

    if booking.status != 'cancelled':
        return Response({'error': 'Refund allowed only for cancelled bookings.'}, status=400)

    try:
        payment = Payment.objects.get(booking=booking)
        payment.status = 'cancelled'
        payment.save()
        return Response({'message': 'Refund processed, payment marked as cancelled.'})
    except Payment.DoesNotExist:
        return Response({'error': 'No payment found for this booking.'}, status=404)
from django.db.models import Q

def get_all_bookings_for_agent(request):
    user_name = request.GET.get('user_name')
    source = request.GET.get('source')
    destination = request.GET.get('destination')
    status = request.GET.get('status')
    category = request.GET.get('category')

    bookings = Booking.objects.select_related('user', 'source', 'destination', 'payment').all()

    # 🔥 Exclude refunded bookings globally unless specifically filtering for cancelled+completed
    if not (status == 'cancelled'):
        bookings = bookings.exclude(payment__status='cancelled')

    # ✅ Filters
    if user_name:
        bookings = bookings.filter(user__display_name__icontains=user_name)
    if source:
        bookings = bookings.filter(source__name__icontains=source)
    if destination:
        bookings = bookings.filter(destination__name__icontains=destination)
    if status:
        if status == 'cancelled':
            bookings = bookings.filter(status='cancelled', payment__status='completed')
        else:
            bookings = bookings.filter(status=status)
    if category:
        bookings = bookings.filter(category=category)

    data = []
    for booking in bookings:
        data.append({
            "booking_id": booking.id,
            "user_id": booking.user.id,
            "user_name": booking.user.display_name,
            "source": booking.source.name if booking.source else "N/A",
            "destination": booking.destination.name,
            "status": booking.status,
            "category": booking.category,
            "booking_date": booking.booking_date,
            "number_of_people": booking.number_of_people,
            "total_price": booking.total_price,
        })

    return JsonResponse({"bookings": data}, status=200)

@api_view(['GET'])
def get_refunds_by_user(request, user_id):
    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    refund_bookings = Booking.objects.filter(
        user=user,
        status='cancelled',
        payment__status='completed'  # Joined filter using related_name on OneToOneField
    )

    result = []
    for booking in refund_bookings:
        result.append({
            "booking_id": booking.id,
            "category": booking.category,
            "source": booking.source.name if booking.source else booking.destination.name,
            "destination": booking.destination.name,
            "number_of_people": booking.number_of_people,
            "total_price": float(booking.total_price),
            "status": booking.status,
            "payment_status": booking.payment.status,
            "booking_date": booking.booking_date.strftime("%Y-%m-%d %H:%M:%S"),
            "transaction_id": booking.payment.transaction_id,
        })

    return Response({"refunds": result}, status=status.HTTP_200_OK)
@api_view(['POST'])
def cancel_booking(request):
    booking_id = request.data.get('booking_id')
    if not booking_id:
        return Response({'error': 'booking_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status == 'cancelled':
        return Response({'message': 'Booking already cancelled.'}, status=status.HTTP_200_OK)

    # Re-add seats or rooms based on category
    if booking.category == 'flight':
        for flight in booking.flights.all():
            flight.available_seats += booking.number_of_people
            flight.save()

    elif booking.category == 'hotel':
            hotel = booking.hotels
            hotel.available_rooms += booking.number_of_people
            hotel.save()

    elif booking.category == 'package':
        try:
            package = booking.packages
            for flight in package.flights.all():
                flight.available_seats += booking.number_of_people
                flight.save()

            for hotel in package.hotels.all():
                hotel.available_rooms += booking.number_of_people
                hotel.save()
        except Package.DoesNotExist:
            return Response({'error': 'Package not found for this booking.'}, status=status.HTTP_404_NOT_FOUND)

    # Mark booking as cancelled
    booking.status = 'cancelled'
    booking.save()

    return Response({'message': 'Booking cancelled and availability updated.'}, status=status.HTTP_200_OK)

@api_view(['GET'])


def get_booking_details(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)

        data = {
            "id": booking.id,
            "user": booking.user.display_name,
            "source": booking.source.name if booking.source else "N/A",
            "destination": booking.destination.name if booking.destination else "N/A",
            "booking_date": booking.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
            "number_of_people": booking.number_of_people,
            "total_price": float(booking.total_price),
            "status": booking.status,
            "category": booking.category,
            "flights": [
                {
                    "flight_number": flight.flight_number,
                    "source": flight.source.name,
                    "destination": flight.destination.name,
                    "price_per_seat": float(flight.price_per_seat),
                    "discount": float(flight.discount),
                    "flight_icon_url": flight.flight_icon_url,
                }
                for flight in booking.flights.all()
            ],
            "hotel": {
                "name": booking.hotels.name,
                "destination": booking.hotels.destination.name,
                "price_per_night": float(booking.hotels.price_per_night),
                "available_rooms": booking.hotels.available_rooms,
                "discount": float(booking.hotels.discount or 0),
                "image_url": booking.hotels.image_url,
            } if booking.hotels else None,
            "package": {
                "name": booking.packages.name,
                "source": booking.packages.source.name,
                "destination": booking.packages.destination.name,
                "price": float(booking.packages.price),
                "discount": float(booking.packages.discount),
                "duration_days": booking.packages.duration_days,
                "image_url": booking.packages.image_url,
            } if booking.packages else None,
        }

        return JsonResponse(data)

    except Booking.DoesNotExist:
        return JsonResponse({"error": "Booking not found."}, status=404)

    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

@csrf_exempt
@require_POST
def create_hotel_booking(request):
    try:
        data = json.loads(request.body)

        user_id = data.get('user_id')
        hotel_id = data.get('hotel_id')
        number_of_people = data.get('number_of_people')
        source_id = data.get('source_id')  # Optional

        if not all([user_id, hotel_id, number_of_people]):
            return JsonResponse({"error": "Missing required fields."}, status=400)

        user = UserProfile.objects.get(id=user_id)
        hotel = Hotel.objects.get(id=hotel_id)
        source = Destination.objects.get(id=source_id) if source_id else None

        discount_multiplier = (1 - float(hotel.discount or 0) / 100)
        final_price = float(hotel.price_per_night) * discount_multiplier * int(number_of_people)

        booking = Booking.objects.create(
            user=user,
            source=source,
            destination=hotel.destination,
            number_of_people=number_of_people,
            total_price=final_price,
            status='pending',
            category='hotel',
            hotels=hotel
        )

        return JsonResponse({
            "message": "Hotel booking created successfully.",
            "booking": {
                "booking_id": booking.id,
                "user": user.display_name,
                "source": source.name if source else None,
                "destination": hotel.destination.name,
                "number_of_people": number_of_people,
                "total_price": final_price,
                "status": booking.status,
                "category": booking.category,
                "hotel": {
                    "id": hotel.id,
                    "name": hotel.name,
                    "destination": hotel.destination.name,
                    "price_per_night": float(hotel.price_per_night),
                    "available_rooms": hotel.available_rooms,
                    "discount": float(hotel.discount or 0),
                    "image_url": hotel.image_url
                }
            }
        })

    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)
    except Hotel.DoesNotExist:
        return JsonResponse({"error": "Hotel not found."}, status=404)
    except Destination.DoesNotExist:
        return JsonResponse({"error": "Invalid source ID."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)


@csrf_exempt
def add_flight(request):
    """Admin can add a new flight."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

    try:
        data = json.loads(request.body)

        flight_number = data.get('flight_number', '').strip()
        source_id = data.get('source')
        destination_id = data.get('destination')
        available_seats = data.get('available_seats')
        price_per_seat = data.get('price_per_seat')
        discount = data.get('discount', 0)

        # ✅ Validate required fields
        if not flight_number or not source_id or not destination_id or available_seats is None or price_per_seat is None:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        if source_id == destination_id:
            return JsonResponse({'error': 'Source and destination cannot be the same'}, status=400)

        # ✅ Check duplicate flight_number
        if Flight.objects.filter(flight_number=flight_number).exists():
            return JsonResponse({'error': 'Flight with this number already exists'}, status=400)

        source = Destination.objects.get(id=source_id)
        destination = Destination.objects.get(id=destination_id)

        # ✅ Create the flight
        flight = Flight.objects.create(
            flight_number=flight_number,
            source=source,
            destination=destination,
            available_seats=available_seats,
            price_per_seat=price_per_seat,
            discount=discount
        )

        return JsonResponse({
            'message': 'Flight added successfully',
            'flight': {
                'id': flight.id,
                'flight_number': flight.flight_number,
                'source': flight.source.name,
                'destination': flight.destination.name,
                'available_seats': flight.available_seats,
                'price_per_seat': str(flight.price_per_seat),
                'discount': str(flight.discount)
            }
        }, status=201)

    except Destination.DoesNotExist:
        return JsonResponse({'error': 'Invalid source or destination ID'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def register_admin(request):
    """Registers an admin user with a temporary password."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

    # ✅ Ensure only an existing admin can create another admin
   

    try:
        # ✅ Parse JSON
        data = json.loads(request.body)

        # ✅ Extract fields
        display_name = data.get('display_name', '').strip()
        phone_number = data.get('phone_number', '').strip()
        location = data.get('location', '').strip()
        email = data.get('email', '').strip()

        # ✅ Minimal validation
        if not display_name:
            return JsonResponse({'error': 'Display name is required'}, status=400)
        if not phone_number or not phone_number.isdigit() or len(phone_number) != 10:
            return JsonResponse({'error': 'Valid 10-digit phone number is required'}, status=400)
        if not location:
            return JsonResponse({'error': 'Location is required'}, status=400)
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        # ✅ Check if user already exists in Firebase
        try:
            firebase_user = auth.get_user_by_email(email)
            return JsonResponse({'error': 'User already registered in Firebase'}, status=400)
        except auth.UserNotFoundError:
            pass  # Proceed with new user creation

        # ✅ Generate a random temporary password
        temp_password = generate_temp_password()

        # ✅ Create admin in Firebase
        firebase_user = auth.create_user(
            email=email,
            password=temp_password,  # Use generated password
            display_name=display_name,
            phone_number=f"+91{phone_number}"
        )

        # ✅ Assign role in Firebase custom claims
        firebase_auth.set_custom_user_claims(firebase_user.uid, {'role': 'admin'})

        # ✅ Store in Django database
        user_profile = UserProfile.objects.create(
            email=firebase_user.email,
            display_name=firebase_user.display_name,
            role='admin',  # Explicitly setting admin role
            phone_number=phone_number,
            location=location
        )

        # ✅ Also add to Admin table
        Admin.objects.create(user_profile=user_profile)

        # ✅ Print temporary password (you can replace this with an email service)
        print(f"Admin {email} registered with temporary password: {temp_password}")

        return JsonResponse({
            'message': 'Admin registered successfully',
            'user': {
                'uid': firebase_user.uid,
                'email': firebase_user.email,
                'role': user_profile.role,
                'temporary_password': temp_password  # This can be removed if sending via email
            }
        }, status=201)

    except firebase_admin.auth.EmailAlreadyExistsError:
        return JsonResponse({'error': 'Email is already registered'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
def register_travel_agent(request):
    """Registers a travel agent with a temporary password."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

    try:
        data = json.loads(request.body)

        # ✅ Extract required fields
        display_name = data.get('display_name', '').strip()
        phone_number = data.get('phone_number', '').strip()
        location = data.get('location', '').strip()
        email = data.get('email', '').strip()

        # ✅ Basic validation
        if not display_name:
            return JsonResponse({'error': 'Display name is required'}, status=400)
        if not phone_number or not phone_number.isdigit() or len(phone_number) != 10:
            return JsonResponse({'error': 'Valid 10-digit phone number is required'}, status=400)
        if not location:
            return JsonResponse({'error': 'Location is required'}, status=400)
        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        # ✅ Check if user already exists
        try:
            firebase_user = firebase_auth.get_user_by_email(email)
            return JsonResponse({'error': 'User already registered in Firebase'}, status=400)
        except firebase_auth.UserNotFoundError:
            pass  # User doesn't exist, continue

        # ✅ Create user in Firebase
        temp_password = generate_temp_password()
        firebase_user = firebase_auth.create_user(
            email=email,
            password=temp_password,
            display_name=display_name,
            phone_number=f"+91{phone_number}"
        )

        # ✅ Set custom Firebase role
        firebase_auth.set_custom_user_claims(firebase_user.uid, {'role': 'travel_agent'})

        # ✅ Store in Django DB
        user_profile = UserProfile.objects.create(
            email=firebase_user.email,
            display_name=firebase_user.display_name,
            role='travel_agent',
            phone_number=phone_number,
            location=location
        )

        # ✅ Create corresponding travel agent entry
        TravelAgent.objects.create(user_profile=user_profile)

        print(f"Travel Agent {email} registered with temporary password: {temp_password}")

        return JsonResponse({
            'message': 'Travel agent registered successfully',
            'user': {
                'uid': firebase_user.uid,
                'email': firebase_user.email,
                'role': user_profile.role,
                'temporary_password': temp_password
            }
        }, status=201)

    except firebase_auth.EmailAlreadyExistsError:
        return JsonResponse({'error': 'Email is already registered'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from .models import UserProfile  # ✅ Import your model

@csrf_exempt
def login_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()

        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)

        # ✅ Firebase login
        firebase_login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(firebase_login_url, json=payload)

        if response.status_code != 200:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

        user = response.json()
        id_token = user['idToken']
        uid = user['localId']

        firebase_user = auth.get_user(uid)
        user_claims = firebase_user.custom_claims or {}
        role = user_claims.get('role', 'user')

        # ✅ Lookup Django user ID from UserProfile using email
        try:
            user_profile = UserProfile.objects.get(email=email)
            user_id = user_profile.id
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'User not found in Django DB'}, status=404)

        session_cookie = auth.create_session_cookie(id_token, expires_in=timedelta(days=5))

        res = JsonResponse({
            'message': 'Login successful',
            'user': {
                'uid': uid,
                'user_id': user_id,  # ✅ Include Django user ID here
                'email': email,
                'role': role,
            }
        })

        res.set_cookie('session', session_cookie, httponly=True, secure=False, samesite='Lax')
        res.set_cookie('refresh_token', user['refreshToken'], httponly=True, secure=False, samesite='Lax')

        return res

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def register_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

    try:
        # ✅ Parse JSON
        data = json.loads(request.body)
        print(data)
        # ✅ Extract fields from request body
        display_name = data.get('display_name', '').strip()
        phone_number = data.get('phone_number', '').strip()
        location = data.get('location', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()  # 🔹 Password needed for Firebase user creation

        # ✅ Minimal backend validation
        if not display_name:
            return JsonResponse({'error': 'Display name is required'}, status=400)

        if not phone_number or not phone_number.isdigit() or len(phone_number) != 10:
            return JsonResponse({'error': 'Valid 10-digit phone number is required'}, status=400)

        if not location:
            return JsonResponse({'error': 'Location is required'}, status=400)

        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        if not password or len(password) < 6:
            return JsonResponse({'error': 'Password must be at least 6 characters long'}, status=400)

        # ✅ Check if user already exists in Firebase
        try:
            firebase_user = auth.get_user_by_email(email)
            return JsonResponse({'error': 'User already registered in Firebase'}, status=400)
        except auth.UserNotFoundError:
            pass  # User doesn't exist, proceed with creation

        # ✅ Create user in Firebase
        firebase_user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
            phone_number=f"+91{phone_number}",  # Assuming Indian phone number format
        )

        # ✅ Store user in Django database
        user_profile = UserProfile.objects.create(
            email=firebase_user.email,
            display_name=firebase_user.display_name,
            role='user', 
            # role='admin' # Default role
            phone_number=phone_number,
            location=location
        )
        # Admin.objects.create(user_profile=user_profile)
        # auth.set_custom_user_claims(firebase_user.uid, {'role': 'admin'})
        firebase_user = auth.get_user(firebase_user.uid)
        print(firebase_user.custom_claims)  # Should output: {'role': 'admin'}


  # Add this import at the top if not already present

     
        return JsonResponse({
            'message': 'User registered successfully',
            'user': {
                'uid': firebase_user.uid,
                'email': firebase_user.email,
                'role': user_profile.role
            }
        }, status=201)

    except firebase_admin.auth.EmailAlreadyExistsError:
        return JsonResponse({'error': 'Email is already registered'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
@csrf_exempt
def forgot_password(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests allowed'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()

        if not email:
            return JsonResponse({'error': 'Email is required'}, status=400)

        # Send password reset email via Firebase
        link = auth.generate_password_reset_link(email)
        # You can customize this to send via your own email service if needed.
        print(f"🔗 Password reset link: {link}")

        return JsonResponse({'message': 'Password reset link sent successfully'}, status=200)

    except auth.UserNotFoundError:
        return JsonResponse({'error': 'No user found with that email'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def get_current_user(request):
    session_cookie = request.COOKIES.get('session')

    if not session_cookie:
        return JsonResponse({'error': 'No session cookie found'}, status=401)

    try:
        # Verify Firebase session cookie
        decoded_claims = auth.verify_session_cookie(session_cookie, check_revoked=True)
        uid = decoded_claims.get('uid')

        firebase_user = auth.get_user(uid)
        email = firebase_user.email
        role = firebase_user.custom_claims.get('role', 'user') if firebase_user.custom_claims else 'user'

        # Optional: Look up UserProfile by email
        try:
            user_profile = UserProfile.objects.get(email=email)
            user_id = user_profile.id
        except UserProfile.DoesNotExist:
            user_id = None  # or handle accordingly

        return JsonResponse({
            'user': {
                'uid': uid,
                'email': email,
                'role': role,
                'user_id': user_id
            }
        })

    except auth.InvalidSessionCookieError:
        return JsonResponse({'error': 'Invalid or expired session cookie'}, status=401)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



