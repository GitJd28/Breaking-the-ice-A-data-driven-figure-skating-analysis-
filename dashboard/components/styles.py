def load_css():
    return """
    <style>

    /* ═══════════════════════════════════════
       GLOBAL BASE
    ═══════════════════════════════════════ */

    @import url('https://fonts.googleapis.com/css2?
    family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main background */
    .stApp {
        background: linear-gradient(
            135deg,
            #0A1628 0%,
            #0D1F3C 50%,
            #0A1628 100%
        );
    }

    /* ═══════════════════════════════════════
       SIDEBAR
    ═══════════════════════════════════════ */

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #060E1E 0%,
            #0A1628 100%
        ) !important;
        border-right: 1px solid rgba(0, 212, 255, 0.15);
    }

    [data-testid="stSidebar"] .stMarkdown p {
        color: #A8C8E8;
        font-size: 0.85rem;
    }

    /* Sidebar nav links */
    [data-testid="stSidebarNav"] a {
        color: #A8C8E8 !important;
        border-radius: 8px;
        transition: all 0.2s ease;
    }

    [data-testid="stSidebarNav"] a:hover {
        background: rgba(0, 212, 255, 0.1) !important;
        color: #00D4FF !important;
    }

    [data-testid="stSidebarNav"] a[aria-selected="true"] {
        background: rgba(0, 212, 255, 0.15) !important;
        color: #00D4FF !important;
        border-left: 3px solid #00D4FF;
    }

    /* ═══════════════════════════════════════
       METRIC CARDS
    ═══════════════════════════════════════ */

    [data-testid="stMetric"] {
        background: linear-gradient(
            135deg,
            rgba(0, 212, 255, 0.08) 0%,
            rgba(15, 32, 64, 0.9) 100%
        );
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 16px;
        padding: 20px 24px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    [data-testid="stMetric"]:hover {
        border-color: rgba(0, 212, 255, 0.5);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.1);
        transform: translateY(-2px);
    }

    [data-testid="stMetricLabel"] {
        color: #7FB3D3 !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="stMetricValue"] {
        color: #00D4FF !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
    }

    /* ═══════════════════════════════════════
       CARDS (custom divs)
    ═══════════════════════════════════════ */

    .ice-card {
        background: linear-gradient(
            135deg,
            rgba(0, 212, 255, 0.06) 0%,
            rgba(15, 32, 64, 0.95) 100%
        );
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }

    .ice-card:hover {
        border-color: rgba(0, 212, 255, 0.35);
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.08);
    }

    .ice-card h3 {
        color: #00D4FF;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .ice-card p {
        color: #A8C8E8;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    /* ═══════════════════════════════════════
       STAT HIGHLIGHT CARDS
    ═══════════════════════════════════════ */

    .stat-card {
        background: linear-gradient(
            135deg,
            rgba(0, 212, 255, 0.12) 0%,
            rgba(0, 212, 255, 0.04) 100%
        );
        border: 1px solid rgba(0, 212, 255, 0.25);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 8px 0;
    }

    .stat-number {
        font-size: 2.5rem;
        font-weight: 800;
        color: #00D4FF;
        line-height: 1;
        margin-bottom: 4px;
    }

    .stat-label {
        font-size: 0.8rem;
        color: #7FB3D3;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 500;
    }

    .stat-sub {
        font-size: 0.75rem;
        color: #4A7FA5;
        margin-top: 4px;
    }

    /* ═══════════════════════════════════════
       PAGE HEADERS
    ═══════════════════════════════════════ */

    .page-header {
        background: linear-gradient(
            135deg,
            rgba(0, 212, 255, 0.15) 0%,
            rgba(0, 100, 180, 0.1) 100%
        );
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 16px;
        padding: 32px 40px;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
    }

    .page-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(
            circle,
            rgba(0, 212, 255, 0.08) 0%,
            transparent 70%
        );
        pointer-events: none;
    }

    .page-header h1 {
        color: #FFFFFF;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }

    .page-header p {
        color: #A8C8E8;
        font-size: 1rem;
        margin: 8px 0 0 0;
    }

    /* ═══════════════════════════════════════
       SECTION HEADERS
    ═══════════════════════════════════════ */

    .section-header {
        color: #FFFFFF;
        font-size: 1.25rem;
        font-weight: 600;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(0, 212, 255, 0.3);
        margin-bottom: 20px;
    }

    /* ═══════════════════════════════════════
       ALERT / INFO BOXES
    ═══════════════════════════════════════ */

    /* Override Streamlit's default alert colors */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: none !important;
    }

    div[data-baseweb="notification"] {
        border-radius: 12px !important;
    }

    /* Info box — icy blue */
    .stAlert [data-baseweb="notification"][kind="info"] {
        background: rgba(0, 212, 255, 0.08) !important;
        border-left: 4px solid #00D4FF !important;
    }

    /* Success box — green ice */
    .stAlert [data-baseweb="notification"][kind="positive"] {
        background: rgba(0, 200, 120, 0.08) !important;
        border-left: 4px solid #00C878 !important;
    }

    /* Warning box — gold */
    .stAlert [data-baseweb="notification"][kind="warning"] {
        background: rgba(243, 156, 18, 0.08) !important;
        border-left: 4px solid #F39C12 !important;
    }

    /* Error box — red */
    .stAlert [data-baseweb="notification"][kind="negative"] {
        background: rgba(231, 76, 60, 0.08) !important;
        border-left: 4px solid #E74C3C !important;
    }

    /* ═══════════════════════════════════════
       DATAFRAMES / TABLES
    ═══════════════════════════════════════ */

    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid rgba(0, 212, 255, 0.15) !important;
    }

    /* ═══════════════════════════════════════
       SLIDERS
    ═══════════════════════════════════════ */

    [data-testid="stSlider"] > div > div > div {
        background: rgba(0, 212, 255, 0.3) !important;
    }

    [data-testid="stSlider"] > div > div > div > div {
        background: #00D4FF !important;
        box-shadow: 0 0 8px rgba(0, 212, 255, 0.5) !important;
    }

    /* ═══════════════════════════════════════
       RADIO BUTTONS
    ═══════════════════════════════════════ */

    [data-testid="stRadio"] label {
        color: #A8C8E8 !important;
    }

    /* ═══════════════════════════════════════
       SELECT BOXES
    ═══════════════════════════════════════ */

    [data-testid="stSelectbox"] label {
        color: #7FB3D3 !important;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ═══════════════════════════════════════
       DIVIDERS
    ═══════════════════════════════════════ */

    hr {
        border: none !important;
        border-top: 1px solid rgba(0, 212, 255, 0.12) !important;
        margin: 28px 0 !important;
    }

    /* ═══════════════════════════════════════
       PLOTLY CHARTS — dark background
    ═══════════════════════════════════════ */

    .js-plotly-plot {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ═══════════════════════════════════════
       FOOTER
    ═══════════════════════════════════════ */

    .footer {
        text-align: center;
        padding: 24px;
        color: #4A7FA5;
        font-size: 0.75rem;
        border-top: 1px solid rgba(0, 212, 255, 0.1);
        margin-top: 48px;
    }

    /* ═══════════════════════════════════════
       INDIA HIGHLIGHT
    ═══════════════════════════════════════ */

    .india-card {
        background: linear-gradient(
            135deg,
            rgba(255, 153, 51, 0.1) 0%,
            rgba(19, 136, 8, 0.1) 100%
        );
        border: 1px solid rgba(255, 153, 51, 0.3);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
    }

    /* ═══════════════════════════════════════
       PROBABILITY DISPLAY
    ═══════════════════════════════════════ */

    .prob-display {
        text-align: center;
        padding: 32px;
        background: linear-gradient(
            135deg,
            rgba(0, 212, 255, 0.08),
            rgba(15, 32, 64, 0.9)
        );
        border-radius: 20px;
        border: 1px solid rgba(0, 212, 255, 0.2);
    }

    .prob-number {
        font-size: 4rem;
        font-weight: 800;
        line-height: 1;
    }

    .prob-label {
        font-size: 0.9rem;
        color: #7FB3D3;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }

    </style>
    """


# ─────────────────────────────────────────────
# Plotly dark theme — apply to every chart
# ─────────────────────────────────────────────

PLOTLY_THEME = dict(
    paper_bgcolor = 'rgba(0,0,0,0)',
    plot_bgcolor  = 'rgba(15, 32, 64, 0.6)',
    font          = dict(
        family = 'Inter, sans-serif',
        color  = '#A8C8E8',
        size   = 12,
    ),
    title = dict(
        font = dict(color='#FFFFFF', size=15),
        x    = 0.01,
    ),
    xaxis = dict(
        gridcolor     = 'rgba(0, 212, 255, 0.08)',
        linecolor     = 'rgba(0, 212, 255, 0.2)',
        tickcolor     = 'rgba(0, 212, 255, 0.2)',
        tickfont      = dict(color='#7FB3D3'),
        title         = dict(font=dict(color='#A8C8E8')),
        zerolinecolor = 'rgba(0, 212, 255, 0.1)',
    ),
    yaxis = dict(
        gridcolor     = 'rgba(0, 212, 255, 0.08)',
        linecolor     = 'rgba(0, 212, 255, 0.2)',
        tickcolor     = 'rgba(0, 212, 255, 0.2)',
        tickfont      = dict(color='#7FB3D3'),
        title         = dict(font=dict(color='#A8C8E8')),
        zerolinecolor = 'rgba(0, 212, 255, 0.1)',
    ),
    legend = dict(
        bgcolor     = 'rgba(10, 22, 40, 0.8)',
        bordercolor = 'rgba(0, 212, 255, 0.2)',
        borderwidth = 1,
        font        = dict(color='#A8C8E8'),
    ),
    colorway = [
        '#00D4FF', '#F39C12', '#E74C3C',
        '#00C878', '#9B59B6', '#1ABC9C',
        '#E67E22', '#3498DB',
    ],
)


def apply_theme(fig, height=450, title=None):
    """Apply consistent dark ice theme to any plotly figure."""
    update = dict(**PLOTLY_THEME, height=height)
    if title:
        update['title'] = dict(
            text  = title,
            font  = dict(color='#FFFFFF', size=15),
            x     = 0.01,
        )
    fig.update_layout(**update)
    return fig
