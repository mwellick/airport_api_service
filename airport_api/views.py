from django.db.models import Count, F, Q
from rest_framework.viewsets import ModelViewSet
from .models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket,
)
from .serializers import (
    CrewSerializer,
    AirportSerializer,
    RouteSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    FlightSerializer,
    OrderSerializer,
    TicketSerializer,
    FlightListSerializer,
    RouteListSerializer,
    FlightRetrieveSerializer,
    RouteRetrieveSerializer,
    TicketListSerializer,
    TicketRetrieveSerializer,
    OrderRetrieveSerializer,
    OrderListSerializer,
)


class CrewViewSet(ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirportViewSet(ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        city = self.request.query_params.get("closest_city")
        if name:
            queryset = queryset.filter(name__icontains=name)
        if city:
            queryset = queryset.filter(closest_big_city__icontains=city)
        return queryset


class RouteViewSet(ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        source = self.request.query_params.get("from")
        destination = self.request.query_params.get("to")
        if source:
            queryset = queryset.filter(
                source__name__icontains=source
            )
        if destination:
            queryset = queryset.filter(
                destination__name__icontains=destination
            )
        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteSerializer
        elif self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteListSerializer


class AirplaneTypeViewSet(ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(
                name__icontains=name
            )
        return queryset


class AirplaneViewSet(ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(
                name__icontains=name
            )
        return queryset


class FlightViewSet(ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        flight_id = self.request.query_params.get("id")
        source = self.request.query_params.get("from")
        destination = self.request.query_params.get("to")
        airplane = self.request.query_params.get("plane_name")
        if flight_id:
            queryset = self.queryset.filter(
                id__in=flight_id
            )
        if source:
            queryset = self.queryset.filter(
                route__source__name__icontains=source
            )
        if destination:
            queryset = self.queryset.filter(
                route__destination__name__icontains=destination
            )
        if airplane:
            queryset = self.queryset.filter(
                airplane__name__icontains=airplane
            )
        if self.action in ("list", "retrieve"):
            return queryset.select_related(
            ).prefetch_related("crews").annotate(
                tickets_available=F(
                    "airplane__rows"
                ) * F(
                    "airplane__seats_in_row"
                ) - Count(
                    "flight_tickets"
                )
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @staticmethod
    def params_to_ints(query_str):
        return [int(str_id) for str_id in query_str.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        ticket_ids = self.request.query_params.get("ticket_id")
        if ticket_ids:
            ticket_ids = self.params_to_ints(ticket_ids)
            queryset = queryset.filter(tickets__id__in=ticket_ids)
        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset.filter(user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        elif self.action == "retrieve":
            return OrderRetrieveSerializer
        return OrderSerializer


class TicketViewSet(ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        queryset = self.queryset
        ticket_id = self.request.query_params.get("id")
        flight_info = self.request.query_params.get("route")
        if ticket_id:
            queryset = self.queryset.filter(
                id__in=ticket_id
            )
        if flight_info:
            queryset = self.queryset.filter(
                Q(flight__route__source__name__icontains=flight_info) |
                Q(flight__route__destination__name__icontains=flight_info)
            )
        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "retrieve":
            return TicketRetrieveSerializer
        return TicketSerializer
