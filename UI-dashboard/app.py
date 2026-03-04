# Urban Heat Island Detection System - Delhi NCR
# Final Year Capstone 2026
# Authors: Farhan Moshin, Aastik Vashistha, Amrit Kaur

import streamlit as st
import streamlit.components.v1 as components
import os
from PIL import Image

# ===========================================================================
#  CONFIG
# ===========================================================================
st.set_page_config(
    page_title="Urban Heat Island Detection System | Delhi NCR",
    page_icon="thermometer",
    layout="wide",
    initial_sidebar_state="expanded"
)

IMAGE_DIR = r"C:\Users\Amrit Kaur\OneDrive\Documents\New Folder\uhi\UHI-Detector\notebooks\images"

CLF_HTML = os.path.join(IMAGE_DIR, "uhi_classification_map_interactive.html")
REG_HTML = os.path.join(IMAGE_DIR, "uhi_regression_map_interactive.html")
CLF_IMG  = os.path.join(IMAGE_DIR, "uhi_classification_map.png")
REG_IMG  = os.path.join(IMAGE_DIR, "uhi_regression_map.png")
FEAT_IMG = os.path.join(IMAGE_DIR, "uhi_feature_importance.png")
PERF_IMG = os.path.join(IMAGE_DIR, "uhi_model_performance.png")
LST_IMG  = os.path.join(IMAGE_DIR, "lst_map.png")
NDBI_IMG = os.path.join(IMAGE_DIR, "ndbi_custom.png")
NDVI_IMG = os.path.join(IMAGE_DIR, "ndvi_custom.png")
DIST_IMG = os.path.join(IMAGE_DIR, "raster_distributions.png")

# ===========================================================================
#  CSS
# ===========================================================================
def inject_css():
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
    else:
        css = "html,body,.stApp{background:#F4F7F9!important;color:#1A2535}"
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

inject_css()

# ===========================================================================
#  HELPERS
# ===========================================================================
def embed_map(path, height=520):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        st.markdown('<div class="map-wrap">', unsafe_allow_html=True)
        components.html(html, height=height, scrolling=False)
        st.markdown("</div>", unsafe_allow_html=True)
        return True
    name = os.path.basename(path)
    st.markdown(
        f'<div style="height:{height}px;background:#F8FAFB;border:2px dashed #C8D4DF;'
        f'border-radius:14px;display:flex;flex-direction:column;align-items:center;'
        f'justify-content:center;gap:10px;color:#8A9BB0;font-family:monospace;font-size:.8rem">'
        f'<div style="font-size:2.5rem;opacity:.3">&#x1F5FA;</div>'
        f'<div style="font-weight:600">{name}</div>'
        f'<div style="font-size:.7rem;opacity:.6">Place this file in IMAGE_DIR to display the real raster overlay</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    return False


def show_img(path, caption=""):
    if os.path.exists(path):
        st.image(Image.open(path), caption=caption, use_container_width=True)
    else:
        st.markdown(
            f'<div style="height:220px;background:#F8FAFB;border:2px dashed #C8D4DF;'
            f'border-radius:10px;display:flex;flex-direction:column;align-items:center;'
            f'justify-content:center;gap:8px;color:#8A9BB0;font-family:monospace;font-size:.75rem">'
            f'<div style="font-size:1.8rem;opacity:.25">&#x1F5BC;</div>'
            f'<div>{os.path.basename(path)}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


def kpi(col, cls, icon, label, value, detail, delta=None):
    delta_html = ""
    if delta:
        delta_html = f'<div class="k-delta">{delta}</div>'
    with col:
        st.markdown(
            f'<div class="kpi {cls}">'
            f'<div class="icon">{icon}</div>'
            f'<div class="k-label">{label}</div>'
            f'<div class="k-value">{value}</div>'
            f'<div class="k-detail">{detail}</div>'
            f'{delta_html}'
            f'</div>',
            unsafe_allow_html=True
        )


def ptitle(text, dot_color="#1CA7A6"):
    return (
        f'<div class="ptitle">'
        f'<span class="dot" style="background:{dot_color}"></span>'
        f'<span class="label">{text}</span>'
        f'</div>'
    )


def section_label(text):
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


def panel_start(title, dot_color="#1CA7A6"):
    st.markdown(f'<div class="panel">{ptitle(title, dot_color)}', unsafe_allow_html=True)

def panel_end():
    st.markdown("</div>", unsafe_allow_html=True)


def page_header(emoji, title, subtitle, breadcrumb=""):
    bc = f'<div class="breadcrumb">{breadcrumb}</div>' if breadcrumb else ""
    st.markdown(
        f'<div class="page-header">'
        f'{bc}'
        f'<h1>{emoji} {title}</h1>'
        f'<div class="sub">{subtitle}</div>'
        f'<div class="divider"></div>'
        f'</div>',
        unsafe_allow_html=True
    )


# ===========================================================================
#  SIDEBAR
# ===========================================================================
with st.sidebar:
    # Brand block
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1CA7A6,#177a7a);'
        'padding:28px 20px 22px;margin-bottom:0">'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:.6rem;'
        'color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:.16em;'
        'margin-bottom:8px">Geospatial Intelligence</div>'
        '<div style="font-size:2rem;font-weight:700;color:#ffffff;line-height:1.2;'
        'letter-spacing:-.2px">Urban Heat Island<br>Detection System</div>'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:.62rem;'
        'color:rgba(255,255,255,.45);margin-top:8px">Delhi NCR &middot; 2026</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div style="padding:8px 12px 4px">'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:.58rem;'
        'text-transform:uppercase;letter-spacing:.14em;color:rgba(255,255,255,.25);'
        'padding:10px 2px 6px">Navigation</div>'
        '</div>',
        unsafe_allow_html=True
    )

    menu = st.radio(
        "Navigation",
        [
            "Risk Classification",
            "Intensity Prediction",
            "Feature Analysis",
            "Hotspot Recommendations",
            "Raw Indices",
            "About",
        ],
        index=0,
        label_visibility="collapsed"
    )

    st.markdown(
        '<div style="padding:16px 20px;margin-top:auto">'
        '<div style="height:1px;background:rgba(255,255,255,.08);margin-bottom:16px"></div>'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:.62rem;'
        'color:rgba(255,255,255,.3);line-height:2.2">'
        '<div><span style="color:#1CA7A6">&#x25CF;</span>  Landsat 8/9 TOA</div>'
        '<div><span style="color:#1CA7A6">&#x25CF;</span>  1,885,534 Pixels</div>'
        '<div><span style="color:#1CA7A6">&#x25CF;</span>  37 Features</div>'
        '<div><span style="color:#1CA7A6">&#x25CF;</span>  LightGBM Ensemble</div>'
        '<div><span style="color:#1CA7A6">&#x25CF;</span>  R&sup2; 0.91 &middot; Acc 91.1%</div>'
        '</div>'
        '<div style="height:1px;background:rgba(255,255,255,.08);margin-top:16px"></div>'
        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:.56rem;'
        'color:rgba(255,255,255,.18);margin-top:10px">Capstone Project &middot; 2026</div>'
        '</div>',
        unsafe_allow_html=True
    )


# ===========================================================================
#  PAGE: RISK CLASSIFICATION
# ===========================================================================
if menu == "Risk Classification":

    page_header(
        "&#x1F525;", "Heat Risk Zone Classification",
        "LightGBM Classifier &mdash; Low / Moderate / High thermal risk zones &middot; "
        "1.88M pixels &middot; Pre-monsoon 2024 &middot; Colormap: RdYlGn_r",
        "Dashboard / Risk Classification"
    )

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    kpi(c1, "hi",  "&#x1F321;", "High Risk Zones",  "56.6%",
        "Dense urban cores &amp; industrial belts", delta="&#x25B2; Dominant class")
    kpi(c2, "md",  "&#x26A1;",  "Moderate Risk",    "28.4%",
        "Urban fringe &amp; mixed-use zones", delta="&#x25CF; Urban fringe")
    kpi(c3, "lo",  "&#x1F33F;", "Low Risk",          "15.0%",
        "Vegetated &amp; water-body proximity", delta="&#x25BC; Yamuna corridor")
    kpi(c4, "cy",  "&#x1F3AF;", "Model Accuracy",   "91.1%",
        "F1-Weighted 0.9146 &middot; Kappa 0.798", delta="&#x2B06; Substantial")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col_map, col_r = st.columns([3, 2], gap="medium")

    with col_map:
        panel_start("Interactive Classification Map &mdash; Real Raster Overlay", "#F05D5E")
        panel_end()
        embed_map(CLF_HTML, height=500)

    with col_r:
        panel_start("Exported Classification Raster", "#1CA7A6")
        show_img(CLF_IMG, "LightGBM Classification Output")
        panel_end()

        st.markdown(
            '<div class="panel">'
            + ptitle("Pixel Distribution by Risk Class", "#F5A623") +
            '<div style="margin-top:4px">'
            '<div class="bar-row"><div class="bar-lbl">High</div>'
            '<div class="bar-track"><div class="bar-fill" style="width:56.6%;'
            'background:linear-gradient(90deg,#F05D5E,#f57f80)"></div></div>'
            '<div class="bar-pct">56.6%</div></div>'
            '<div class="bar-row"><div class="bar-lbl">Moderate</div>'
            '<div class="bar-track"><div class="bar-fill" style="width:28.4%;'
            'background:linear-gradient(90deg,#F5A623,#f7c46a)"></div></div>'
            '<div class="bar-pct">28.4%</div></div>'
            '<div class="bar-row"><div class="bar-lbl">Low</div>'
            '<div class="bar-track"><div class="bar-fill" style="width:15%;'
            'background:linear-gradient(90deg,#4CAF50,#7ecf82)"></div></div>'
            '<div class="bar-pct">15.0%</div></div>'
            '</div></div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="insight">'
        '<strong>Key Finding:</strong> Over half the NCR pixel mass falls in the High-Risk band '
        '(UHII &gt; 5&deg;C), concentrated in dense urban cores of <strong>East Delhi, Rohini, '
        'Gurgaon Industrial Estate</strong> and <strong>Faridabad</strong>. The 15% Low-Risk '
        'fraction correlates with the Yamuna floodplain, Asola Wildlife Sanctuary, and South Delhi '
        'ridge forests. Colormap <strong>RdYlGn_r</strong> &mdash; '
        'Green = Low &middot; Yellow = Moderate &middot; Red = High.'
        '</div>'
        '<div class="lineage">'
        '<span>Landsat 8 TOA Band 10/11</span>'
        '<span>GEE May&ndash;Jun 2024</span>'
        '<span>RdYlGn_r colormap</span>'
        '<span>LightGBM Classifier v3.3</span>'
        '<span>EPSG:4326</span>'
        '</div>',
        unsafe_allow_html=True
    )


# ===========================================================================
#  PAGE: INTENSITY PREDICTION
# ===========================================================================
elif menu == "Intensity Prediction":

    page_header(
        "&#x1F321;", "UHI Intensity Prediction",
        "LightGBM Regressor &mdash; Continuous UHII (&deg;C) deviation from rural baseline &middot; "
        "Colormap: RdYlBu_r &mdash; Blue = Cool &middot; Yellow = Moderate &middot; Red = Extreme Heat",
        "Dashboard / Intensity Prediction"
    )

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    kpi(c1, "hi", "&#x1F53A;", "Peak Intensity",  "+15.20&deg;C",
        "Max recorded pixel deviation", delta="&#x25B2; Shahdara hotspot")
    kpi(c2, "md", "&#x1F4CA;", "Mean UHII",        "+4.92&deg;C",
        "Avg across all urban pixels", delta="&#x25B2; 3.4% vs baseline")
    kpi(c3, "lo", "&#x1F33E;", "Rural Baseline",  "37.30&deg;C",
        "Non-urban reference LST", delta="&#x25CF; Pre-monsoon 2024")
    kpi(c4, "cy", "&#x2705;",  "R&sup2; Score",    "0.9060",
        "RMSE 0.83&deg;C &middot; MAE 0.63&deg;C", delta="&#x25B2; Excellent fit")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    col_map, col_r = st.columns([3, 2], gap="medium")

    with col_map:
        panel_start("Interactive Intensity Map &mdash; Real Raster Overlay", "#F05D5E")
        panel_end()
        loaded = embed_map(REG_HTML, height=500)
        if not loaded:
            embed_map(os.path.join(IMAGE_DIR, "uhi_regression_map.html"), height=500)

    with col_r:
        panel_start("Regression Raster Output", "#1CA7A6")
        show_img(REG_IMG, "LightGBM Regression &mdash; UHII (&deg;C)")
        panel_end()

        st.markdown(
            '<div class="panel">'
            + ptitle("Top Intensity Zones", "#F05D5E") +
            '<table class="dtable">'
            '<thead><tr><th>Zone</th><th>Peak UHII</th><th>Mean</th><th>Risk</th></tr></thead>'
            '<tbody>'
            '<tr><td>East Delhi</td><td>+15.2&deg;C</td><td>+11.4&deg;C</td><td><span class="badge hi">HIGH</span></td></tr>'
            '<tr><td>Connaught Pl.</td><td>+13.8&deg;C</td><td>+10.9&deg;C</td><td><span class="badge hi">HIGH</span></td></tr>'
            '<tr><td>Faridabad Ind.</td><td>+12.5&deg;C</td><td>+9.8&deg;C</td><td><span class="badge hi">HIGH</span></td></tr>'
            '<tr><td>Gurgaon Udyog</td><td>+11.1&deg;C</td><td>+9.0&deg;C</td><td><span class="badge hi">HIGH</span></td></tr>'
            '<tr><td>Rohini</td><td>+10.7&deg;C</td><td>+8.4&deg;C</td><td><span class="badge hi">HIGH</span></td></tr>'
            '<tr><td>Noida Sec 62</td><td>+8.3&deg;C</td><td>+6.1&deg;C</td><td><span class="badge md">MOD</span></td></tr>'
            '</tbody></table></div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="insight">'
        '<strong>Gradient Analysis:</strong> The sharpest UHII gradients occur at the boundary '
        'between the <strong>Yamuna floodplain</strong> and <strong>East Delhi\'s built-up '
        'fabric</strong> &mdash; a 9.6&deg;C delta over less than 2 km. Blue cool islands '
        'correspond to the Yamuna river channel, Bhalswa Lake, and Sanjay Van forest. '
        'The regressor captures these transitions with RMSE = 0.83&deg;C.'
        '</div>'
        '<div class="lineage">'
        '<span>Landsat 8 TOA Band 10/11</span>'
        '<span>GEE May&ndash;Jun 2024</span>'
        '<span>RdYlBu_r colormap &middot; 2nd&ndash;98th pct</span>'
        '<span>LightGBM Regressor v3.3</span>'
        '<span>R&sup2;: 0.906 &middot; RMSE: 0.83&deg;C</span>'
        '</div>',
        unsafe_allow_html=True
    )


# ===========================================================================
#  PAGE: FEATURE ANALYSIS
# ===========================================================================
elif menu == "Feature Analysis":

    page_header(
        "&#x1F4CA;", "Model Interpretability &amp; Feature Analysis",
        "SHAP-informed importance across 37 engineered features &middot; "
        "Grouped by Urban Morphology, Biological, and Geographic categories",
        "Dashboard / Feature Analysis"
    )

    tab1, tab2, tab3 = st.tabs(["Feature Importance", "Model Metrics", "Feature Groups"])

    with tab1:
        col_i, col_e = st.columns([2, 1], gap="medium")

        with col_i:
            panel_start("Feature Importance Plot &mdash; LightGBM Gain", "#F5A623")
            show_img(FEAT_IMG, "Top-20 features by Gain score")
            panel_end()

            panel_start("Input Raster Distributions", "#1CA7A6")
            show_img(DIST_IMG, "Pixel-level histograms of key input bands")
            panel_end()

        with col_e:
            features = [
                ("1. NDBI_local_std",   "95%",
                 "Variance of Built-up Index in a local kernel. High variance signals dense urban "
                 "canyons that trap long-wave radiation &mdash; the #1 heat driver."),
                ("2. DEM (Elevation)",  "82%",
                 "Lower elevation = hotter pooling zones via cold-air drainage. Aravalli ridges "
                 "and Yamuna floodplain are consistently cooler in LST imagery."),
                ("3. NDVI",             "75%",
                 "Evapotranspiration from green cover suppresses LST. The single most effective "
                 "natural cooling signal across all model runs."),
                ("4. Emissivity_B10",   "68%",
                 "Impervious surfaces have lower emissivity giving higher apparent LST. "
                 "Physics-based feature ensuring thermodynamic accuracy."),
                ("5. NDBI x NDVI",      "60%",
                 "Engineered cross-term capturing the inverse urban&ndash;vegetation relationship. "
                 "The strongest non-linear thermal driver in the model."),
            ]
            cards_html = "".join(
                f'<div class="fcrd">'
                f'<div class="fn">{fn}</div>'
                f'<div class="fw">{fw}</div>'
                f'<div class="fbar" style="width:{w}"></div>'
                f'</div>'
                for fn, w, fw in features
            )
            st.markdown(
                '<div class="panel">'
                + ptitle("Top Feature Cards", "#1CA7A6")
                + cards_html + "</div>",
                unsafe_allow_html=True
            )

    with tab2:
        cr, cc = st.columns(2, gap="medium")
        with cr:
            st.markdown(
                '<div class="panel">'
                + ptitle("Regression &mdash; LightGBM Regressor", "#4CAF50") +
                '<div class="prow"><span class="pk">R&sup2; Score</span>'
                '<span class="pv" style="color:#4CAF50">0.9060</span></div>'
                '<div class="prow"><span class="pk">RMSE</span><span class="pv">0.8263&deg;C</span></div>'
                '<div class="prow"><span class="pk">MAE</span><span class="pv">0.6282&deg;C</span></div>'
                '<div class="prow"><span class="pk">Max Error</span><span class="pv">3.41&deg;C</span></div>'
                '<div class="prow"><span class="pk">Train Pixels</span><span class="pv">1.51 M</span></div>'
                '<div class="prow"><span class="pk">Test Pixels</span><span class="pv">377 K</span></div>'
                '<div class="prow"><span class="pk">CV Strategy</span><span class="pv">5-Fold Spatial</span></div>'
                '</div>',
                unsafe_allow_html=True
            )
        with cc:
            st.markdown(
                '<div class="panel">'
                + ptitle("Classification &mdash; LightGBM Classifier", "#1CA7A6") +
                '<div class="prow"><span class="pk">Accuracy</span>'
                '<span class="pv" style="color:#1CA7A6">91.1%</span></div>'
                '<div class="prow"><span class="pk">F1 (Weighted)</span><span class="pv">0.9146</span></div>'
                '<div class="prow"><span class="pk">Cohen\'s Kappa</span><span class="pv">0.7982</span></div>'
                '<div class="prow"><span class="pk">Precision (High)</span><span class="pv">0.924</span></div>'
                '<div class="prow"><span class="pk">Recall (High)</span><span class="pv">0.937</span></div>'
                '<div class="prow"><span class="pk">AUC (OvR macro)</span><span class="pv">0.968</span></div>'
                '<div class="prow"><span class="pk">Kappa Interpret</span><span class="pv">Substantial</span></div>'
                '</div>',
                unsafe_allow_html=True
            )

        panel_start("Performance Plots &mdash; Confusion Matrix &amp; Residual Analysis", "#F05D5E")
        show_img(PERF_IMG, "Model validation plots from testing phase")
        panel_end()

    with tab3:
        section_label("Feature Categories")
        groups = [
            ("#F05D5E", "Urban Morphology", "14 features",
             ["NDBI", "NDBI_local_std", "Urban_Canyon_Proxy", "Imperviousness_Index",
              "Built-up Fraction", "B10 (TIR)", "B11 (TIR)", "Emissivity_B10/B11",
              "Thermal_Anisotropy", "Road_Density_proxy"]),
            ("#4CAF50", "Vegetation &amp; Water", "12 features",
             ["NDVI", "PV (Veg fraction)", "NDWI", "Moisture Index", "ET_proxy",
              "Green_Canopy_Cover", "Water_Dist_km", "SAVI", "EVI", "Riparian_Buffer", "LSWI"]),
            ("#1CA7A6", "Geography &amp; Physics", "11 features",
             ["DEM (Elevation)", "Slope", "Aspect", "Sky_View_Factor",
              "NDBI x NDVI cross-term", "LST_Physics_correction",
              "Lat/Lon encoded", "Distance_to_centre_km", "Terrain_Wetness_Index"]),
        ]
        gcols = st.columns(3, gap="medium")
        for col, (color, title, count, feats) in zip(gcols, groups):
            feat_items = "".join(
                f'<div style="padding:3px 0;font-size:.8rem;color:#4A5E72;'
                f'border-bottom:1px solid #EEF2F5;line-height:1.5">{f}</div>'
                for f in feats
            )
            with col:
                st.markdown(
                    f'<div style="background:#FFFFFF;border:1px solid #E2E8EF;'
                    f'border-top:3px solid {color};border-radius:14px;padding:20px;'
                    f'box-shadow:0 1px 4px rgba(30,42,56,.07)">'
                    f'<div style="font-family:\'JetBrains Mono\',monospace;color:{color};'
                    f'font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;'
                    f'font-weight:600;margin-bottom:4px">{title}</div>'
                    f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:.6rem;'
                    f'color:#8A9BB0;margin-bottom:14px">{count}</div>'
                    f'<div>{feat_items}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )


# ===========================================================================
#  PAGE: HOTSPOT RECOMMENDATIONS
# ===========================================================================
elif menu == "Hotspot Recommendations":

    page_header(
        "&#x1F4CD;", "Hotspot Analysis &amp; Mitigation Simulator",
        "Evidence-based urban heat mitigation strategies + interactive impact estimator "
        "derived from model outputs and published urban climate literature",
        "Dashboard / Hotspot Recommendations"
    )

    # ---- Simulator (dark navy panel) ----------------------------------------
    st.markdown(
        '<div class="sim-panel">'
        '<div class="sim-title">Mitigation Impact Simulator</div>',
        unsafe_allow_html=True
    )

    s1, s2, s3 = st.columns(3, gap="medium")
    with s1:
        zone_sel = st.selectbox("Select Zone", [
            "East Delhi / Shahdara  (+15.2 C)",
            "Okhla Industrial  (+13.8 C)",
            "Faridabad Corridor  (+12.5 C)",
            "Rohini Sub-City  (+10.7 C)",
            "Gurgaon Udyog Vihar  (+11.1 C)",
        ])
    with s2:
        strategy = st.selectbox("Select Strategy", [
            "Cool Roofs (High-Albedo Paint)",
            "Urban Tree Planting (+% canopy)",
            "Green Roofs on Buildings",
            "Permeable Pavements",
            "Reflective Road Surfaces",
            "Water Feature / Blue Infrastructure",
        ])
    with s3:
        adopt = st.slider("Adoption Intensity (%)", 10, 80, 30, 5)

    st.markdown("</div>", unsafe_allow_html=True)

    base_t = {
        "East Delhi / Shahdara  (+15.2 C)": 15.2,
        "Okhla Industrial  (+13.8 C)": 13.8,
        "Faridabad Corridor  (+12.5 C)": 12.5,
        "Rohini Sub-City  (+10.7 C)": 10.7,
        "Gurgaon Udyog Vihar  (+11.1 C)": 11.1,
    }
    coeff = {
        "Cool Roofs (High-Albedo Paint)": .040,
        "Urban Tree Planting (+% canopy)": .050,
        "Green Roofs on Buildings": .035,
        "Permeable Pavements": .025,
        "Reflective Road Surfaces": .030,
        "Water Feature / Blue Infrastructure": .045,
    }

    b    = base_t[zone_sel]
    red  = round(b * coeff[strategy] * (adopt / 100) * 10, 2)
    new  = round(b - red, 2)
    drop = round((red / b) * 100, 1)

    r1, r2, r3, r4 = st.columns(4, gap="medium")
    kpi(r1, "hi", "&#x1F321;", "Current UHII",    f"+{b}&deg;C",   zone_sel.split("(")[0].strip())
    kpi(r2, "lo", "&#x1F4C9;", "Est. Reduction",   f"&minus;{red}&deg;C", f"{strategy} @ {adopt}%")
    kpi(r3, "cy", "&#x2705;",  "Post-Mitigation",  f"+{new}&deg;C", "Projected UHII after intervention")
    kpi(r4, "md", "&#x1F4CA;", "Improvement",      f"{drop}%",      "Temperature drop achieved")

    st.markdown(
        f'<div class="insight">'
        f'<strong>Simulation Result:</strong> Applying <strong>{strategy}</strong> at '
        f'<strong>{adopt}% adoption</strong> across '
        f'<strong>{zone_sel.split("(")[0].strip()}</strong> is estimated to reduce peak UHII by '
        f'<strong>&minus;{red}&deg;C</strong> ({drop}%), from '
        f'<strong>+{b}&deg;C &rarr; +{new}&deg;C</strong>. '
        f'Coefficients from Santamouris et al. (2014) and Mohajerani et al. (2017).'
        f'</div>',
        unsafe_allow_html=True
    )

    section_label("Priority Hotspots")

    hotspots = [
        {"n": 1, "z": "Shahdara / East Delhi", "d": "East Delhi",
         "pk": "+15.2&deg;C", "mn": "+11.4&deg;C", "pop": "2.1M", "area": "28 km&sup2;",
         "it": "Cool Roofs Programme + Street Tree Corridors",
         "wy": "High imperviousness (NDBI &gt; 0.6), near-zero NDVI. A 20% cool-roof adoption could reduce LST by 1.5&ndash;2.0&deg;C based on albedo-emissivity modelling.",
         "st": "Priority 1"},
        {"n": 2, "z": "Okhla Industrial Area", "d": "South-East Delhi",
         "pk": "+13.8&deg;C", "mn": "+10.2&deg;C", "pop": "0.3M", "area": "12 km&sup2;",
         "it": "Green Roofs on Industrial Sheds + Waste Heat Audit",
         "wy": "Industrial process heat compounds solar gain. Insulated green roofs + exhaust rerouting estimated to cut UHII by 2&ndash;3&deg;C.",
         "st": "Priority 2"},
        {"n": 3, "z": "Faridabad Industrial Corridor", "d": "Faridabad, Haryana",
         "pk": "+12.5&deg;C", "mn": "+9.8&deg;C", "pop": "1.4M", "area": "45 km&sup2;",
         "it": "Urban Green Belt + Permeable Pavement Mandate",
         "wy": "30% of area is sealed surface. Permeable paving + boulevard trees increases latent heat flux, reducing peak temp by ~1.8&deg;C.",
         "st": "Priority 3"},
        {"n": 4, "z": "Rohini Sub-City", "d": "North-West Delhi",
         "pk": "+10.7&deg;C", "mn": "+8.4&deg;C", "pop": "1.8M", "area": "35 km&sup2;",
         "it": "Neighbourhood Parks + Blue-Green Corridor Network",
         "wy": "Isolated green patches lack connectivity. A 5m tree belt between sectors creates evaporative cooling corridors of &Delta;LST &asymp; &minus;1.2&deg;C.",
         "st": "Priority 4"},
        {"n": 5, "z": "Gurgaon Udyog Vihar", "d": "Gurugram, Haryana",
         "pk": "+11.1&deg;C", "mn": "+9.0&deg;C", "pop": "0.5M", "area": "20 km&sup2;",
         "it": "Reflective Glass Coating + Vertical Greenery on Towers",
         "wy": "Curtain-wall towers reflect solar radiation into canyons. Low-albedo coatings + vertical gardens estimated to cut UHII by 1.5&deg;C.",
         "st": "Priority 5"},
    ]

    for h in hotspots:
        st.markdown(
            f'<div class="hcard">'
            f'<div class="hh">'
            f'<div>'
            f'<div class="hr">&#x25CF; {h["st"]}</div>'
            f'<div class="ht">{h["z"]}</div>'
            f'<div style="margin-top:7px;display:flex;align-items:center;gap:8px">'
            f'<span class="badge teal">{h["d"]}</span>'
            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:.62rem;color:#8A9BB0">'
            f'{h["area"]} &middot; Pop. {h["pop"]}</span>'
            f'</div></div>'
            f'<div>'
            f'<div class="hpk">{h["pk"]}</div>'
            f'<div class="hsb">Peak &middot; Mean {h["mn"]}</div>'
            f'</div></div>'
            f'<div class="hint">'
            f'<div class="hil">&#x25B6; Recommended Intervention</div>'
            f'<div class="hit">{h["it"]}</div>'
            f'<div class="hiw">{h["wy"]}</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="insight">'
        '<strong>Combined Impact:</strong> Implementing all 5 interventions could reduce mean NCR '
        'UHII by <strong>1.2&ndash;1.8&deg;C</strong> and benefit over '
        '<strong>6 million residents</strong> during peak summer months (April&ndash;June).'
        '</div>',
        unsafe_allow_html=True
    )


# ===========================================================================
#  PAGE: RAW INDICES
# ===========================================================================
elif menu == "Raw Indices":

    page_header(
        "&#x1F5C4;", "Raw Spectral Indices &amp; Distributions",
        "Source raster bands used as model inputs &middot; Landsat 8 TOA &middot; Pre-monsoon 2024",
        "Dashboard / Raw Indices"
    )

    section_label("Input Raster Layers")

    c1, c2 = st.columns(2, gap="medium")
    items = [
        (c1, "LST &mdash; Land Surface Temperature", "#F05D5E", LST_IMG,
         "Absolute LST (&deg;C) across Delhi NCR"),
        (c2, "NDBI &mdash; Normalized Difference Built-up Index", "#F5A623", NDBI_IMG,
         "High values = Dense Urban Built-up"),
        (c1, "NDVI &mdash; Normalized Difference Vegetation Index", "#4CAF50", NDVI_IMG,
         "Green = Dense Vegetation &middot; Brown = Bare/Urban"),
        (c2, "Raster Distributions &mdash; Pixel Histograms", "#1CA7A6", DIST_IMG,
         "Pixel value histograms for key input bands"),
    ]
    for col, title, dot, img, cap in items:
        with col:
            panel_start(title, dot)
            show_img(img, cap)
            panel_end()

    st.markdown(
        '<div class="insight">'
        '<strong>Index Relationships:</strong> Strong negative correlation between NDVI and LST '
        '(r &asymp; &minus;0.73) and positive correlation between NDBI and LST (r &asymp; +0.68) '
        'confirm that vegetation suppression and built-up expansion are the twin thermal drivers '
        'across Delhi NCR. Both are encoded into the 37-feature matrix as raw features '
        'and engineered interactions.'
        '</div>'
        '<div class="lineage">'
        '<span>Landsat 8 TOA USGS L1TP</span>'
        '<span>GEE v0.1.370</span>'
        '<span>Bands B4 B5 B6 B10 B11</span>'
        '<span>May&ndash;Jun 2024</span>'
        '<span>30m Spatial Resolution</span>'
        '</div>',
        unsafe_allow_html=True
    )


# ===========================================================================
#  PAGE: ABOUT
# ===========================================================================
elif menu == "About":

    page_header(
        "&#x2139;", "Urban Heat Island Detection System",
        "Delhi NCR &middot; "
        "LightGBM Ensemble + Landsat 8/9 Satellite Imagery",
        "Dashboard / About"
    )

    # Hero banner
    st.markdown(
        '<div class="about-hero">'
        '<div class="hero-tag">&#x1F30D; About This Project</div>'
        '<h2>Advanced Geospatial Intelligence<br>for Urban Climate Analysis</h2>'
        '<p>'
        'The Urban Heat Island (UHI) Detection System is an advanced geospatial intelligence '
        'platform designed to detect, quantify, and classify urban heat intensity across the '
        'Delhi NCR region using multi-temporal Landsat 8/9 satellite imagery.'
        '<br><br>'
        'The system integrates spectral indices, physical surface parameters, and spatial '
        'morphology features within a LightGBM ensemble framework to generate high-resolution '
        'UHI intensity predictions and risk classifications. In addition to predictive analytics, '
        'the platform provides hotspot identification and mitigation simulation tools, enabling '
        'evidence-based urban cooling strategies.'
        '</p>'
        '</div>',
        unsafe_allow_html=True
    )

    col_a, col_b = st.columns([3, 2], gap="medium")

    with col_a:
        section_label("Technical Specifications")
        specs = [
            ("Data Source",         "Google Earth Engine &middot; Landsat 8 TOA"),
            ("Acquisition Window",  "April &ndash; June 2024 (Pre-Monsoon)"),
            ("Spatial Coverage",    "Delhi NCR &mdash; ~55,000 km&sup2;"),
            ("Spatial Resolution",  "30 m per pixel (resampled)"),
            ("Total Pixels",        "1,885,534"),
            ("Features Engineered", "37 (spectral + physics + spatial)"),
            ("Models Deployed",     "LightGBM Regressor + Classifier"),
            ("Map Embed Method",    "streamlit.components.v1.html() &mdash; real Folium HTML"),
            ("UI Stack",            "Streamlit + Folium + GEE Python API"),
            ("Project Year",        "2026"),
        ]
        rows_html = "".join(
            f'<div class="prow"><span class="pk">{k}</span><span class="pv">{v}</span></div>'
            for k, v in specs
        )
        panel_start("Project Specifications", "#1CA7A6")
        st.markdown(rows_html, unsafe_allow_html=True)
        panel_end()

        section_label("UHII Classification Thresholds")
        st.markdown(
            '<div class="panel">'
            '<div class="prow">'
            '<span class="pk"><span class="badge lo">LOW</span></span>'
            '<span class="pv" style="color:#4CAF50">UHII &le; 2.0&deg;C</span>'
            '</div>'
            '<div class="prow">'
            '<span class="pk"><span class="badge md">MODERATE</span></span>'
            '<span class="pv" style="color:#F5A623">2.0 &lt; UHII &le; 5.0&deg;C</span>'
            '</div>'
            '<div class="prow">'
            '<span class="pk"><span class="badge hi">HIGH</span></span>'
            '<span class="pv" style="color:#F05D5E">UHII &gt; 5.0&deg;C</span>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    with col_b:
        section_label("Methodology Pipeline")
        step_colors = ["#F05D5E","#F5A623","#F5A623","#F5A623",
                       "#4CAF50","#4CAF50","#1CA7A6","#1CA7A6","#1CA7A6","#1CA7A6"]
        steps = [
            "Landsat 8/9 collection via GEE",
            "Cloud masking + TOA calibration",
            "LST retrieval &mdash; Split-Window Algorithm",
            "UHII = LST_urban &minus; LST_rural_baseline",
            "37-feature matrix engineering",
            "LightGBM training (80/20 stratified)",
            "Spatial 5-fold cross-validation",
            "SHAP interpretability analysis",
            "Folium HTML raster export (Jupyter)",
            "Streamlit embed via components.html()",
        ]
        steps_html = "".join(
            f'<div style="display:flex;gap:12px;align-items:flex-start;padding:8px 0;'
            f'border-bottom:1px solid #E2E8EF">'
            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:.65rem;'
            f'color:{step_colors[i]};font-weight:700;flex-shrink:0;'
            f'background:rgba(28,167,166,.08);padding:2px 7px;border-radius:4px">{i+1:02d}</span>'
            f'<span style="font-size:.82rem;color:#4A5E72;line-height:1.5">{s}</span></div>'
            for i, s in enumerate(steps)
        )
        panel_start("Step-by-Step Pipeline", "#F5A623")
        st.markdown(steps_html, unsafe_allow_html=True)
        panel_end()

    # Team section
    section_label("Project Team")
    t1, t2, t3 = st.columns(3, gap="medium")
    team = [
        (t1, "&#x1F9D1;&#x200D;&#x1F4BB;", "Farhan Moshin",""),
        (t2, "&#x1F9D1;&#x200D;&#x1F4BB;", "Aastik Vashistha",""),
        (t3, "&#x1F9D1;&#x200D;&#x1F4BB;", "Amrit Kaur",""),
    ]
    for col, icon, name, role in team:
        with col:
            st.markdown(
                f'<div class="team-card">'
                f'<div class="avatar">{icon}</div>'
                f'<div class="name">{name}</div>'
                f'<div class="role">{role}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown(
        '<div class="lineage" style="margin-top:32px">'
        '<span>Landsat 8 TOA USGS L1TP</span>'
        '<span>GEE v0.1.370</span>'
        '<span>LightGBM v3.3.5</span>'
        '<span>Streamlit v1.35</span>'
        '<span>Folium v0.16</span>'
        '<span>System v5.0 &middot; 2026</span>'
        '</div>',
        unsafe_allow_html=True
    )