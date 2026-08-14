def load_css():
    return """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Base */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #F0F4FA;
    }

    /* Hide default streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2D5BFF 0%, #3D7EFF 100%) !important;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    [data-testid="stSidebarNav"] a {
        color: #E0E9FF !important;
        border-radius: 10px;
        padding: 8px 12px !important;
        transition: all 0.2s ease;
    }

    [data-testid="stSidebarNav"] a:hover {
        background: rgba(255,255,255,0.15) !important;
    }

    [data-testid="stSidebarNav"] a[aria-selected="true"] {
        background: #FFFFFF !important;
        color: #2D5BFF !important;
        font-weight: 600;
    }

    /* Metric cards — white with soft shadow */
    [data-testid="stMetric"] {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(61, 126, 255, 0.08);
        border: 1px solid rgba(61, 126, 255, 0.08);
    }

    [data-testid="stMetricLabel"] {
        color: #6B7B99 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricValue"] {
        color: #1A2B4A !important;
        font-size: 1.9rem !important;
        font-weight: 700 !important;
    }

    /* Custom cards */
    .info-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 12px rgba(61, 126, 255, 0.08);
        border: 1px solid rgba(61, 126, 255, 0.08);
        margin: 8px 0;
        height: 100%;
    }

    .info-card h3 {
        color: #1A2B4A;
        font-size: 1rem;
        font-weight: 700;
        margin: 0 0 8px 0;
    }

    .info-card p {
        color: #6B7B99;
        font-size: 0.88rem;
        line-height: 1.6;
        margin: 0;
    }

    /* Stat highlight card (blue gradient) */
    .stat-card-blue {
        background: linear-gradient(135deg, #3D7EFF 0%, #2D5BFF 100%);
        border-radius: 16px;
        padding: 24px;
        color: #FFFFFF;
        box-shadow: 0 4px 20px rgba(61, 126, 255, 0.25);
    }

    .stat-card-blue .num {
        font-size: 2.4rem;
        font-weight: 800;
        line-height: 1;
    }

    .stat-card-blue .lbl {
        font-size: 0.8rem;
        opacity: 0.9;
        margin-top: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .stat-card-blue .sub {
        font-size: 0.72rem;
        opacity: 0.75;
        margin-top: 4px;
    }

    /* Page header */
    .page-title {
        color: #1A2B4A;
        font-size: 1.75rem;
        font-weight: 800;
        margin: 8px 0 4px 0;
    }

    .page-subtitle {
        color: #6B7B99;
        font-size: 0.95rem;
        margin-bottom: 24px;
    }

    /* Section headers */
    .section-title {
        color: #1A2B4A;
        font-size: 1.15rem;
        font-weight: 700;
        margin: 24px 0 12px 0;
    }

    /* Alerts — softer */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: none !important;
    }

    /* Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        border: 1px solid rgba(61, 126, 255, 0.1) !important;
        overflow: hidden;
    }

    /* Dividers */
    hr {
        border: none !important;
        border-top: 1px solid rgba(61, 126, 255, 0.1) !important;
        margin: 24px 0 !important;
    }

    /* Chart container */
    .js-plotly-plot {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 2px 12px rgba(61, 126, 255, 0.08);
    }

    /* India callout — saffron/green Indian flag palette */
    .india-callout {
        background: linear-gradient(135deg, #FFF5EC 0%, #F0FDF4 100%);
        border-left: 4px solid #FF9933;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
    }

    .india-callout p {
        color: #1A2B4A;
        font-size: 0.95rem;
        line-height: 1.6;
        margin: 0;
    }

    /* Probability display */
    .prob-box {
        background: #FFFFFF;
        border-radius: 20px;
        padding: 32px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(61, 126, 255, 0.1);
    }

    .prob-num {
        font-size: 4rem;
        font-weight: 800;
        line-height: 1;
    }

    .prob-verdict {
        font-size: 0.9rem;
        font-weight: 700;
        margin-top: 8px;
        letter-spacing: 0.1em;
    }

    .prob-detail {
        font-size: 0.85rem;
        color: #6B7B99;
        margin-top: 12px;
    }

    /* Sidebar logo */
    .sidebar-logo {
        text-align: center;
        padding: 20px 0 24px 0;
        border-bottom: 1px solid rgba(255,255,255,0.15);
        margin-bottom: 16px;
    }

    .sidebar-logo .icon {
        font-size: 2.5rem;
    }

    .sidebar-logo .name {
        font-weight: 800;
        font-size: 1.2rem;
        margin-top: 8px;
        letter-spacing: -0.02em;
    }

    .sidebar-logo .tag {
        font-size: 0.7rem;
        opacity: 0.8;
        margin-top: 4px;
    }

    </style>
    """


# Plotly light theme
PLOTLY_LIGHT_THEME = dict(
    paper_bgcolor = 'rgba(0,0,0,0)',
    plot_bgcolor  = '#FFFFFF',
    font          = dict(
        family = 'Inter, sans-serif',
        color  = '#1A2B4A',
        size   = 12,
    ),
    xaxis = dict(
        gridcolor     = 'rgba(61, 126, 255, 0.08)',
        linecolor     = 'rgba(61, 126, 255, 0.2)',
        tickfont      = dict(color='#6B7B99'),
        title         = dict(font=dict(color='#1A2B4A', size=12)),
        zerolinecolor = 'rgba(61, 126, 255, 0.1)',
    ),
    yaxis = dict(
        gridcolor     = 'rgba(61, 126, 255, 0.08)',
        linecolor     = 'rgba(61, 126, 255, 0.2)',
        tickfont      = dict(color='#6B7B99'),
        title         = dict(font=dict(color='#1A2B4A', size=12)),
        zerolinecolor = 'rgba(61, 126, 255, 0.1)',
    ),
    legend = dict(
        bgcolor     = 'rgba(255,255,255,0.9)',
        bordercolor = 'rgba(61, 126, 255, 0.15)',
        borderwidth = 1,
        font        = dict(color='#1A2B4A', size=11),
    ),
    colorway = [
        '#3D7EFF',   # blue
        '#FF9933',   # saffron
        '#00C878',   # green
        '#F39C12',   # gold
        '#E74C3C',   # red
        '#9B59B6',   # purple
        '#1ABC9C',   # teal
        '#E67E22',   # orange
    ],
    margin = dict(l=40, r=20, t=40, b=40),
)


def apply_theme(fig, height=400):
    """Apply light theme to any plotly figure."""
    fig.update_layout(**PLOTLY_LIGHT_THEME, height=height)
    return fig


# Chart color constants
CHART_COLORS = {
    'primary'   : '#3D7EFF',
    'gold'      : '#F39C12',
    'silver'    : '#95A5A6',
    'bronze'    : '#CD7F32',
    'no_medal'  : '#B8C5D6',
    'accent'    : '#FF9933',
    'success'   : '#00C878',
    'danger'    : '#E74C3C',
    'text'      : '#1A2B4A',
    'muted'     : '#6B7B99',
}

MEDAL_COLORS_LIGHT = {
    'Gold'    : '#F39C12',
    'Silver'  : '#95A5A6',
    'Bronze'  : '#CD7F32',
    'No Medal': '#B8C5D6',
}