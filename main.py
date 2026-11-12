from drafter import *
from bakery import assert_equal
from dataclasses import dataclass, field


@dataclass
class Scenario:
    """Stores one completed traffic calculation along with it's orginal data
    and name."""
    intersection_name: str
    intersection_pattern: str
    north_south_traffic_volume: int
    east_west_traffic_volume: int
    cycle_length: float
    north_south_percentage: float
    east_west_percentage: float
    north_south_green: float
    east_west_green: float


@dataclass
class State:
    """Stores current information and previously saved scenarios,
    uses the field(default_factory) function from drafter website to ensure
    that multiple instances can be created and saved."""
    saved_scenarios: list[Scenario] = field(default_factory=list)
    current_intersection_name: str = ""
    selected_pattern: str = "Two movement groups"
    current_north_south_volume: int = 0
    current_east_west_volume: int = 0
    current_cycle_length: float = 0.0
    current_north_south_percentage: float = 0.0
    current_east_west_percentage: float = 0.0
    current_east_west_green: float = 0.0
    current_north_south_green: float = 0.0

def calculate_north_south_percentage(north_south_volume: int, east_west_volume: int)->float:
    """
    Calculates the North/South percentage of total traffic
    """
    total_volume = north_south_volume + east_west_volume
    percentage = (north_south_volume / total_volume) * 100
    return round(percentage, 1)

def calculate_east_west_percentage(north_south_volume: int, east_west_volume: int)->float:
    """
    Calculates the East/West percentage of total traffic by adding the volumes together then dividing the East/West volume by the total
    and rounding it
    """
    total_volume = north_south_volume + east_west_volume
    percentage = (east_west_volume / total_volume) * 100
    return round(percentage, 1)

def calculate_green_time(percentage: float, cycle_length: float)->float:
    """Calculates the estimated green time for one direction"""
    green_time = (percentage / 100) * cycle_length
    return round(green_time,1)

assert_equal(
    calculate_north_south_percentage(60, 40),
    60.0
)

assert_equal(
    calculate_east_west_percentage(60, 40),
    40.0
)

assert_equal(
    calculate_green_time(60.0, 100.0),
    60.0
)

def create_graph_bar(label: str, percentage: float,
                     color: str) -> Div:
    """
    Creates a colored bar representing a traffic percentage.
    Uses Drafter styling options to control the bar appearance.
    """

    bar = Div(
        "",
        style_background_color=color,
        style_width=str(percentage) + "%",
        style_height="20px",
        style_border_radius="5px"
    )

    graph = Div(
        bar,
        style_background_color="#E5E7EB",
        style_width="100%",
        style_height="20px",
        style_border_radius="5px"
    )

    return Div(
        Text(label),
        graph
    )
                
    
    
@route
def index(state: State) -> Page:
    """Displays the home page of the application."""
    return Page(state, [
        "Welcome to the Traffic Light Timing Calculator!",
        "This website estimates traffic light time distribution "
        "between two directions of movement.",
        Button("Start", "intersection_info")
    ])


@route
def intersection_info(state: State) -> Page:
    """Collects the intersection name and selected pattern."""
    return Page(state, [
        Header("Intersection Information"),
        "Enter a name for your intersection:",
        TextBox("intersection_name"),
        "Choose your intersection pattern:",
        SelectBox(
            "pattern",
            ["Two movement groups"],
            state.selected_pattern
        ),
        Button("Continue", "save_intersection")
    ])


@route
def save_intersection(
    state: State,
    intersection_name: str,
    pattern: str
) -> Page:
    """Saves the intersection information into State."""
    state.current_intersection_name = intersection_name
    state.selected_pattern = pattern

    return traffic_input(state)


@route
def traffic_input(state: State) -> Page:
    """Collects traffic volumes and the cycle length."""
    return Page(state, [
        Header("Traffic Information"),
        "Intersection: " + state.current_intersection_name,

        "Enter North/South vehicles per hour:",
        TextBox(
            "north_south_volume",
            state.current_north_south_volume,
            "number"
        ),

        "Enter East/West vehicles per hour:",
        TextBox(
            "east_west_volume",
            state.current_east_west_volume,
            "number"
        ),

        "Enter the total signal cycle length in seconds:",
        TextBox(
            "cycle_length",
            state.current_cycle_length,
            "number"
        ),

        Button("Calculate Timings", "calculate_timings")
    ])


@route
def calculate_timings(
    state: State,
    north_south_volume: int,
    east_west_volume: int,
    cycle_length: float
) -> Page:
    """Validates and saves the traffic information."""

    state.current_north_south_volume = north_south_volume
    state.current_east_west_volume = east_west_volume
    state.current_cycle_length = cycle_length

    if north_south_volume < 0 or east_west_volume < 0:
        return Page(state, [
            Header("Invalid Traffic Volume"),
            "Traffic volumes cannot be negative.",
            Button("Go Back", "traffic_input")
        ])

    if cycle_length <= 0:
        return Page(state, [
            Header("Invalid Cycle Length"),
            "The cycle length must be greater than zero.",
            Button("Go Back", "traffic_input")
        ])

    if north_south_volume + east_west_volume == 0:
        return Page(state, [
            Header("No Traffic Entered"),
            "At least one traffic volume must be greater than zero.",
            Button("Go Back", "traffic_input")
        ])
    
    state.current_north_south_percentage = (
        calculate_north_south_percentage(north_south_volume,east_west_volume))
    
    state.current_east_west_percentage = (
        calculate_east_west_percentage(north_south_volume,east_west_volume))
    
    state.current_north_south_green = calculate_green_time(
        state.current_north_south_percentage, cycle_length)
    
    state.current_east_west_green = calculate_green_time(
        state.current_east_west_percentage, cycle_length)
    
    return results(state)


@route
def results(state: State) -> Page:
    """Displays the traffic information entered by the user."""
    return Page(state, [
        Header("Estimated Traffic Light Timings"),
        
        "Intersection: " + state.current_intersection_name,
        
        "North/South Volume: " + str(state.current_north_south_volume),
        
        "East/West Volume: " + str(state.current_east_west_volume),
        
        "Cycle Length: " + str(state.current_cycle_length) + " seconds",
        
        "North/South Traffic: " + str(state.current_north_south_percentage) + "%",
        
        "East/West Traffic: " + str(state.current_east_west_percentage) + "%",
        
        "Estimated North/South Green Time: " + str(state.current_north_south_green) + " seconds",
        
        "Estimated East/West Green Time: " + str(state.current_east_west_green) + " seconds",
        
        Button("Edit Traffic Information", "traffic_input"),

        Button("Save This Scenario", "save_scenario"),

        Button("View Saved Scenarios", "saved_scenarios"),

        Button("Display Graph", "display_graph"),

        Button("Return Home", "index")
        
        ])

@route
def save_scenario(state:State)->Page:
    """Saves the current traffic calculation as a scenario."""
    scenario = Scenario(
        state.current_intersection_name,
        state.selected_pattern,
        state.current_north_south_volume,
        state.current_east_west_volume,
        state.current_cycle_length,
        state.current_north_south_percentage,
        state.current_east_west_percentage,
        state.current_north_south_green,
        state.current_east_west_green
    )
    
    state.saved_scenarios.append(scenario)
    
    return Page(state, [
        Header("Scenario Saved!"),
        "Your intersection calculation has been saved.",
        Button("View Saved Scenarios","saved_scenarios"),
        Button("Return to Results","results"),
        Button("Calculate Another Intersection", "intersection_info")
        ])

@route
def saved_scenarios(state:State)->Page:
    """Displays all previously saved traffic scenarios"""
    content = [ Header("Saved Intersection Scenarios")]
    
    if len(state.saved_scenarios) == 0:
        content.append("You have not saved any scenarios yet.")
    else:
        for scenario in state.saved_scenarios:
            content.append(Header(scenario.intersection_name))
            
            content.append("North/South Traffic: " +
                           str(scenario.north_south_traffic_volume)
                           )
            content.append("East/West Traffic: " +
                           str(scenario.east_west_traffic_volume)
                           )
            content.append("Cycle Length: " +
                           str(scenario.cycle_length) + " seconds"
                           )
            content.append("North/South Green Time: " +
                           str(scenario.north_south_green) + " seconds"
                           )
            content.append("East/West Green Time: " +
                           str(scenario.east_west_green) + " seconds"
                           )
    content.append(Button("Display Graph", "display_graph"))
    content.append(Button("Calculate Another Intersection", "intersection_info"))
    content.append(Button("Return Home", "index"))
    
    return Page(state,content)

@route

@route
def display_graph(state: State) -> Page:
    """Displays bar graphs comparing saved traffic timings."""

    content = [
        Header("Traffic Timing Comparison"),
        "Comparing Green Light Distribution Across Intersections."
    ]

    if len(state.saved_scenarios) == 0:
        content.append("No saved scenarios available.")

    else:
        for scenario in state.saved_scenarios:
            content.append(Header(scenario.intersection_name))

            north_south_percentage = (
                scenario.north_south_green /
                scenario.cycle_length * 100
            )

            east_west_percentage = (
                scenario.east_west_green /
                scenario.cycle_length * 100
            )

            content.append(
                Text(
                    "North/South: " +
                    str(scenario.north_south_green) + " seconds"
                )
            )

            content.append(
                create_graph_bar(
                    "North/South",
                    north_south_percentage,
                    "seagreen"
                )
            )

            content.append(
                Text(
                    "East/West: " +
                    str(scenario.east_west_green) +
                    " seconds"
                )
            )

            content.append(
                create_graph_bar(
                    "East/West",
                    east_west_percentage,
                    "steelblue"
                )
            )

    content.append(
        Button("Return to Saved Scenarios", "saved_scenarios")
    )

    content.append(
        Button("Calculate Another Intersection", "intersection_info")
    )

    content.append(
        Button("Return Home", "index")
    )

    return Page(state, content)

set_site_information(
    author="Harrison Cottom",
    description="An educational traffic timing calculator",
    sources=[],
    planning=["Harrison Cottom CS1 Final Project Concept.pdf","Harrison Cottom CS1 Final Project 1_ Design.pdf"],
    links=["https://github.com/HarrisonCottom/CS106-Final-Project"]
)
hide_debug_information()
set_website_framed(False)
start_server(State())
