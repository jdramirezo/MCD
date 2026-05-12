use color_eyre::Result;
use crossterm::event::{self, Event, KeyCode};
use ratatui::{
    DefaultTerminal,
    layout::{Constraint, Direction, Layout},
    style::{Color, Modifier, Style},
    widgets::{Block, Borders, List, ListItem, ListState, Paragraph},
};

/* Memory management  */

struct App {
    countries: Vec<Country>,    /* List of countries to display */
    selected: usize,            /* Index of the currently selected country */
    should_quit: bool,          /* True when user presses q */
}

struct Country {
    name: String,              /* Name of the country */
    score: f64,                /* Score of the country */
}

/* This creates the initial "state of the" app and instatiates the structs */

impl App {
    fn new() -> Self {
        Self {
            countries: vec![
                Country {
                    name: "Switzerland".to_string(),
                    score: 0.75,
                },
                Country {
                    name: "Luxembourg".to_string(),
                    score: 0.65,
                },
                Country {
                    name: "Norway".to_string(),
                    score: 0.56,
                },
                Country {
                    name: "Sweden".to_string(),
                    score: 0.58,
                },
            ],
            selected: 0,
            should_quit: false,
        }
    }
    fn next(&mut self) {
    self.selected = (self.selected + 1) % self.countries.len();
    }
    fn previous(&mut self) {
        if self.selected == 0 {
            self.selected = self.countries.len() - 1;
        } else {
            self.selected -= 1;
        }
    }   
}

fn main() -> Result<()> {
    color_eyre::install()?;

    let terminal = ratatui::init();
    let result = run(terminal);
    ratatui::restore();

    result
}

/* This is the main run loop of the app, it draws the UI and handles user input */

fn run(mut terminal: DefaultTerminal) -> Result<()> {
    /* Initialize the app */
    let mut app = App::new();
    while !app.should_quit {
        /* Draw the UI */
        terminal.draw(|frame| {
            /* Get the area of the frame */
            let area = frame.area();
            /* Split the area into chunks therefore chunk[0] and chunk[1] are left and right panels */
            let chunks = Layout::default()
                .direction(Direction::Horizontal)
                .constraints([
                    Constraint::Percentage(40),
                    Constraint::Percentage(60),
                ])
                .split(area);
            /* Create a list of ListItem from the countries in the app, meaning transfor the list to ratatui list items */
            let items: Vec<ListItem> = app
                .countries
                .iter()
                .map(|country| {
                    ListItem::new(format!("{} - {:.2}", country.name, country.score))
                })
                .collect();
            /* Create a state for the list, Ratatui needs ListState to know which item is selected.*/
            let mut list_state = ListState::default();
            list_state.select(Some(app.selected));
            /*Build the list widget, .block adds a border and title, .highlight_style adds styling to the selected item */
            let list = List::new(items)
                .block(Block::default().title("Countries").borders(Borders::ALL))
                .highlight_style(
                    Style::default()
                        .fg(Color::Yellow)
                        .add_modifier(Modifier::BOLD),
                )
                .highlight_symbol("> ");
            
            /* Render the list widget, this draws the list on the left panel chunk[0] 
            why stateful? because we need to keep track of the selected item */
            frame.render_stateful_widget(list, chunks[0], &mut list_state);
            /* Get the selected country from the app using the selected index */
            let selected_country = &app.countries[app.selected];
            /* Build the details panel on the right chunk */
            let details = Paragraph::new(format!(
                "Selected country: {}\n\nScore: {:.2}\n\nThis screen could show TOPSIS, ELECTRE, weights, criteria, etc.\n\nPress ↑ / ↓ to navigate.\nPress q to quit.",
                selected_country.name,
                selected_country.score
            ))
            /* .block adds a border and title */
            .block(Block::default().title("Details").borders(Borders::ALL));
            /* Render the details panel on the right chunk */
            frame.render_widget(details, chunks[1]);
        })?;

        /* Read key events 
            q      quit
            Down   move down
            Up     move up
            other  do nothing*/

        if let Event::Key(key) = event::read()? {
            match key.code {
                KeyCode::Char('q') => app.should_quit = true,
                KeyCode::Down => app.next(),
                KeyCode::Up => app.previous(),
                _ => {}
            }
        }
    }

    Ok(())
}