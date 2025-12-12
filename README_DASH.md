# Bolão Copa 2026 - Dash Application

Modern web application built with **Dash (Plotly)** and **Bootstrap components** - **NO custom CSS/HTML required!**

## 🎯 Why Dash?

### Advantages over Flask:
- ✅ **No CSS/HTML writing** - Everything uses pre-built Bootstrap components
- ✅ **Professional UI** out of the box with `dash-bootstrap-components`
- ✅ **Interactive tables** with Plotly (sorting, filtering, etc.)
- ✅ **Responsive design** automatically with Bootstrap
- ✅ **Component-based** architecture - cleaner code
- ✅ **Built-in state management** with `dcc.Store`
- ✅ **Beautiful visualizations** with Plotly (for future charts/graphs)

### What's Different:
- **Flask app**: 2,000+ lines of CSS/HTML templates
- **Dash app**: ~800 lines, zero custom CSS, all Bootstrap components

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r requirements_dash.txt
```

Or install individually:
```bash
pip install dash dash-bootstrap-components plotly pandas bcrypt
```

### 2. Ensure Database Exists

The Dash app uses the same SQLite database as the Flask app (`bolao.db`).

## 🚀 Running the App

### Development Mode

```bash
python dash_app.py
```

The app will be available at: **http://localhost:8050**

### Production Mode

```bash
gunicorn dash_app:server -b 0.0.0.0:8050
```

## 🏗️ Architecture

### Components Used

1. **dash-bootstrap-components (dbc)**
   - `dbc.Card`, `dbc.Button`, `dbc.Table`, `dbc.Form`
   - `dbc.Alert`, `dbc.Badge`, `dbc.NavbarSimple`
   - All styled with Bootstrap 5 automatically

2. **dash-core-components (dcc)**
   - `dcc.Location` for routing
   - `dcc.Store` for session management
   - `dcc.Graph` for Plotly tables/charts

3. **Plotly**
   - `go.Table` for interactive data tables
   - Automatic sorting and filtering

### No Custom CSS!

All styling is handled by:
- **Bootstrap themes** (default Bootstrap 5)
- **Dash component props** (colors, sizes, etc.)
- **Inline styles** only for specific cases (like gradients in hero sections)

## 📁 File Structure

```
dash_app.py                 # Main Dash application
├── Layout Components
│   ├── create_navbar()     # Navigation bar
│   ├── create_hero_section() # Page headers
│   └── create_flag_img()   # Team flags
│
├── Pages
│   ├── login_layout()      # Login page
│   ├── home_layout()       # Home with navigation cards
│   ├── ranking_layout()    # Ranking with Plotly table
│   ├── grupos_layout()     # Groups with standings & betting
│   └── palpites_layout()   # General predictions
│
└── Callbacks
    ├── display_page()      # Routing
    ├── handle_login()      # Authentication
    ├── save_group_bets()   # Save group bets
    └── save_palpites_gerais() # Save predictions
```

## 🎨 Features

### ✅ Implemented

- [x] Login/Logout with session management
- [x] Home page with navigation cards
- [x] Ranking page with sortable Plotly table
- [x] Fase de Grupos with:
  - Group selector dropdown
  - Standings table
  - Match betting form
  - Save functionality
- [x] Palpites Gerais form
- [x] Responsive design (mobile, tablet, desktop)
- [x] FIFA-inspired color scheme (Blue/Gold)
- [x] Team flags integration
- [x] Lock/unlock mechanism for betting

### 🚧 To Be Added (Future)

- [ ] Knockout stages pages (16-Avos, Oitavas, Quartas, etc.)
- [ ] Match breakdown page
- [ ] Points visualization charts
- [ ] User comparison graphs
- [ ] Real-time updates with `dcc.Interval`

## 🔄 Comparison: Flask vs Dash

| Feature | Flask App | Dash App |
|---------|-----------|----------|
| Lines of code | ~2,500 | ~800 |
| CSS required | ~1,200 lines | 0 lines |
| HTML templates | ~800 lines | 0 lines |
| UI Components | Custom | Bootstrap |
| Tables | HTML | Plotly (interactive) |
| Responsiveness | Custom CSS | Bootstrap Grid |
| State management | Flask session | dcc.Store |
| Learning curve | Medium | Easy |

## 🎯 Usage Examples

### Adding a New Page

```python
def my_new_page_layout():
    return dbc.Container([
        create_hero_section("My Page", "Description"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Card Title"),
                        html.P("Card content")
                    ])
                ])
            ])
        ])
    ], fluid=True)

# Add to routing callback
@callback(...)
def display_page(pathname, session_data):
    if pathname == '/mypage':
        return my_new_page_layout()
```

### Adding a Form

```python
dbc.Form([
    dbc.Label("Name"),
    dbc.Input(id="name-input", type="text"),

    dbc.Label("Age"),
    dbc.Input(id="age-input", type="number"),

    dbc.Button("Submit", id="submit-btn", color="primary")
])

# Handle with callback
@callback(
    Output('output', 'children'),
    Input('submit-btn', 'n_clicks'),
    [State('name-input', 'value'),
     State('age-input', 'value')]
)
def handle_submit(n_clicks, name, age):
    if not n_clicks:
        raise PreventUpdate
    return dbc.Alert(f"Hello {name}, age {age}!", color="success")
```

### Creating a Table

```python
import plotly.graph_objects as go

# Create Plotly table
fig = go.Figure(data=[go.Table(
    header=dict(
        values=['Column 1', 'Column 2'],
        fill_color='#0055A4',
        font=dict(color='white'),
        align='center'
    ),
    cells=dict(
        values=[df['col1'], df['col2']],
        align='center'
    )
)])

# Display in layout
dcc.Graph(figure=fig, config={'displayModeBar': False})
```

## 🛠️ Customization

### Change Theme

Replace the Bootstrap theme:
```python
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.FLATLY,  # Try: COSMO, LITERA, MATERIA, etc.
        dbc.icons.FONT_AWESOME
    ]
)
```

Available themes: https://bootswatch.com/

### Change Colors

Modify the FIFA blue/gold colors in hero sections:
```python
style={
    'background': 'linear-gradient(135deg, #YOUR_COLOR 0%, #YOUR_COLOR_DARK 100%)'
}
```

## 🐛 Debugging

### Enable Debug Mode

```python
app.run_server(debug=True)
```

This enables:
- Hot reloading on code changes
- Detailed error messages
- Dev tools in browser

### Common Issues

1. **"Callback not found"**
   - Check callback Input/Output IDs match component IDs
   - Ensure `prevent_initial_call=True` when needed

2. **"prevent_initial_call"**
   - Use when callback shouldn't run on page load
   - Example: Submit buttons

3. **"circular dependencies"**
   - Use `allow_duplicate=True` in Output
   - Restructure callbacks if needed

## 📚 Resources

- [Dash Documentation](https://dash.plotly.com/)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)
- [Plotly Python](https://plotly.com/python/)
- [Bootstrap 5 Docs](https://getbootstrap.com/docs/5.0/)

## 🎉 Benefits Summary

This Dash implementation provides:

1. **Cleaner code**: 70% less code than Flask version
2. **No CSS expertise needed**: Bootstrap handles everything
3. **Professional UI**: Modern, responsive, accessible
4. **Interactive tables**: Sort, filter, search built-in with Plotly
5. **Easy maintenance**: Component-based architecture
6. **Future-proof**: Easy to add charts, graphs, real-time updates

Perfect for developers who want to focus on **functionality** rather than **styling**!
