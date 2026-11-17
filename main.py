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
    Calculates the North/South percentage of total traffic by adding both traffic volumes and divinding
    the north south volume by the total, and converts the results to a percentage rouded to one decimal.
    The total traffic volume must be greater than zero.

    Arguments:
        north_south_volume(int): The number of North/South vehicles per hour.
        east_west_volume(int): The number of East/West vehicals per hour.

    Returns:
        float: The North/South traffic percentage, from 0.0 to 100.0.
    """
    total_volume = north_south_volume + east_west_volume
    percentage = (north_south_volume / total_volume) * 100
    return round(percentage, 1)

assert_equal(calculate_north_south_percentage(60, 40), 60.0)
assert_equal(calculate_north_south_percentage(25, 75), 25.0)
assert_equal(calculate_north_south_percentage(1, 2), 33.3)

def calculate_east_west_percentage(north_south_volume: int, east_west_volume: int)->float:
    """
    Calculates the East/West percentage of total traffic by adding the volumes together then dividing the 
    East/West volume by the total and rounding it.

    Arguments: 
        north_south_volume(int):The number of North/South vehicals per hou.
        east_west_volume(int): The number of East/West vehicles per hour.

    Returns:
        float: The East/West traffic percentage, from 0.0 to 100.0.
    """
    total_volume = north_south_volume + east_west_volume
    percentage = (east_west_volume / total_volume) * 100
    return round(percentage, 1)

assert_equal(calculate_east_west_percentage(60, 40), 40.0)
assert_equal(calculate_east_west_percentage(25, 75), 75.0)
assert_equal(calculate_east_west_percentage(1, 2), 66.7)

def calculate_green_time(percentage: float, cycle_length: float)->float:
    """
    Calculates the estimated green time for one direction by multiplying the traffic percentage
    by the full cycle length and rounds the result to one decimal place.

    Arguments:
        percentage(float): The direction's share of total traffic as a percentage from 0.0 to 100.0.

    Returns:
        float: The estimated green-light time in seconds.
    """
    green_time = (percentage / 100) * cycle_length
    return round(green_time,1)

assert_equal(calculate_green_time(60.0, 100.0), 60.0)
assert_equal(calculate_green_time(25.0, 80.0), 20.0)
assert_equal(calculate_green_time(33.3, 90.0), 30.0)

def create_graph_bar(label: str, percentage: float,
                     color: str) -> Div:
    """
    Creates a colored bar representing a traffic percentage.
    Uses Drafter styling options to control the bar appearance. It creates a colored inner bar whose width matches
    the percentage, and places it inside a full-wdith gray background bar, and displays the supplied label.

    Arguments:
        label (str): The direction name displayed beside the bar.
        percentage(float): The percentage represented by the bar.
        color(str): The background color used for the filled portion.

    Returns:
        Div: A Drafter Div containing the label and the graph bar which can be displayed on a page
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
                
assert_equal(isinstance(create_graph_bar("North/South", 60.0, "seagreen"), Div), True)
assert_equal(isinstance(create_graph_bar("East/West", 40.0, "steelblue"), Div), True)
assert_equal(isinstance(create_graph_bar("North/South", 0.0, "red"), Div), True)    
    
@route
def index(state: State) -> Page:
    """   
    Displays the home page of the application explains the purpose of the calculator,
    and provides a button to begin entering intersection information.

    Arguments:
        state(State): The current application state.

    Returns:
        Page: The application's welcome page.
    """
    return Page(state, [
        "Welcome to the Traffic Light Timing Calculator!",
        "This website estimates traffic light time distribution "
        "between two directions of movement.",
        Button("Start", "intersection_info")
    ])

assert_equal(isinstance(index(State()), Page), True)
assert_equal(isinstance(index(State(current_intersection_name="Main Street")), Page), True)
assert_equal(isinstance(index(State(saved_scenarios=[])), Page), True)

@route
def intersection_info(state: State) -> Page:
    """
    Displays the form for entering intersection information by building
    a page where the user can enter an intersection name and choose a pattern and commits it 
    to the state.

    Arguments: 
        state(State): The current applicaiton state, including the seleteced intersection pattern.

    Returns:
        Page: THe intersection information entry page.
    
    """
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

assert_equal(isinstance(intersection_info(State()), Page), True)
assert_equal(isinstance(intersection_info(State(selected_pattern="Two movement groups")), Page), True)
assert_equal(isinstance(intersection_info(State(current_intersection_name="Main Street")), Page), True)

@route
def save_intersection(
    state: State,
    intersection_name: str,
    pattern: str
) -> Page:
    """
    Saves the intersection name and patttern in the application state. It does this
    by updating the current intersection name and selected pttern in State, then
    opens the traffic-volume input page.

    Arguments:
        state(State): The current application state.
        intersection_name(str): The name entered for the intersection.
        pattern(str): The selected intersection movement pattern.

    Returns:
        Page: The traffic information entry page.
    
    """
    state.current_intersection_name = intersection_name
    state.selected_pattern = pattern

    return traffic_input(state)

state = State()
page = save_intersection(state, "Main Street", "Two movement groups")
assert_equal(state.current_intersection_name, "Main Street")
assert_equal(state.selected_pattern, "Two movement groups")
assert_equal(isinstance(page, Page), True)

@route
def traffic_input(state: State) -> Page:
    """
    Displays the form for entering traffic volumes and cycle length by creating
    a page with three inputs for north/south traffic and east/west traffic along with 
    the total signal length.

    Arguments:
        state(State): The current application state, including the intersection name 
        and any previously entered traffic values.

    Returns:
        Page: The traffic information entry page.
    """
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

assert_equal(isinstance(traffic_input(State()), Page), True)
assert_equal(isinstance(traffic_input(State(current_intersection_name="Main Street")), Page), True)
assert_equal(isinstance(traffic_input(State(current_north_south_volume=120)), Page), True)

@route
def calculate_timings(
    state: State,
    north_south_volume: int,
    east_west_volume: int,
    cycle_length: float
) -> Page:
    """
    Validates and saves the traffic information by saving entered values,
    checking traffic volume and cycle length validity, and if the total traffic is 
    greater than 0. If values are valid, it calls calculation functions for traffic percentage
    to calculate green light timing.

    Arguments:
        state(State):The current application state to update.
        north_south_volume(int): North/South vehicals per hour.
        east_west_volume(int): East/West vehicals per hour.
        cycle_length(float): The full signal cycle length in seconds.

    Returns:
        Page: An error page if an input is invalid; otherwise, the results
        page containing the calculated traffic timings.
    """

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

state = State()
page = calculate_timings(state, 60, 40, 100.0)
assert_equal(state.current_north_south_percentage, 60.0)
assert_equal(state.current_east_west_green, 40.0)
assert_equal(isinstance(page, Page), True)

@route
def results(state: State) -> Page:
    """
    Displays the calculated traffic percentages and green-light times by building a results
    page showing traffic volumes, cycle length, traffic percentages, and estimated green-light times.
    It also provides navigation buttons to edit, save, graph, or return home.

    Arguments:
        state(State):The current application state containing the intersection
        information and calculated results.

    Returns:
        Page: The traffic calculation results page.
    """
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

assert_equal(isinstance(results(State()), Page), True)
assert_equal(isinstance(results(State(current_intersection_name="Main Street")), Page), True)
assert_equal(isinstance(results(State(current_north_south_green=30.0, current_east_west_green=70.0)), Page), True)

@route
def save_scenario(state:State)->Page:
    """
    Saves the current traffic calculation as a scenario by creating
    an instance of Scenario using the current intersection data, it adds it to
    the saved_scenarios list, and displays a confirmation page.

    Arguments:
        state(State): The current application state containing the 
        intersection information and calculated timings.

    Returns:
        Page: A confirmation page showing that the scenario was saved. 
    """
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

state = State(current_intersection_name="Main Street",
              current_north_south_volume=60,
              current_east_west_volume=40,
              current_cycle_length=100.0,
              current_north_south_percentage=60.0,
              current_east_west_percentage=40.0,
              current_north_south_green=60.0,
              current_east_west_green=40.0)
page = save_scenario(state)
assert_equal(len(state.saved_scenarios), 1)
assert_equal(state.saved_scenarios[0].intersection_name, "Main Street")
assert_equal(isinstance(page, Page), True)

@route
def saved_scenarios(state:State)->Page:
    """
    Displays all previously saved traffic scenarios from the current session
    by building a page listing each saved intersection and its traffic volumes, cycle length,
    and estimated green-light times. If no scenarios have been saved, it displays a message.

    Arguments:
        state(State): The current application state containing saved Scenario objects.

    Returns:
        Page: The saved scenarios page.
    """
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

assert_equal(isinstance(saved_scenarios(State()), Page), True)
state = State()
state.saved_scenarios.append(Scenario("Main Street", "Two movement groups", 60, 40, 100.0, 60.0, 40.0, 60.0, 40.0))
assert_equal(isinstance(saved_scenarios(state), Page), True)
assert_equal(len(state.saved_scenarios), 1)

@route
def display_graph(state: State) -> Page:
    """
    Displays bar graphs comparing saved traffic timings percentages. For
    each saved scenario, calculates the percentage of the cycle assigned to 
    each direction and creates a colored comparison bar. If there are no
    saved scenarios, it displays a message instead.

    Arguments:
        state(State): The current application state containing saved Scenario objects.

    Returns:
        Page: The traffic timing comparison graph page.
    """

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

assert_equal(isinstance(display_graph(State()), Page), True)

state = State()
state.saved_scenarios.append(Scenario("Main Street", "Two movement groups",
                                     60, 40, 100.0, 60.0, 40.0, 60.0, 40.0))
assert_equal(isinstance(display_graph(state), Page), True)
assert_equal(len(state.saved_scenarios), 1)

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
