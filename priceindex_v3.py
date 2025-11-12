import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config("🎄 Preis-Index Dashboard", layout="wide")

# Replace plain title with logo + title side by side
col_title, col_logo = st.columns([3, 1])
with col_title:
    st.title("🍪 Wie teuer sind 🎄Weihnachtskekse? 🎅")
with col_logo:
    st.image("WIFO_logo.png", use_container_width=True)

# ---------------------------------------------------
# 1. LOAD EUROSTAT DATA
# ---------------------------------------------------
@st.cache_data
def load_hicp_data():
    df = pd.read_csv("prc_hicp_midx_clean.csv")
    extracted = df["date"].astype(str).str.extract(r"^(?P<Y>\d{4})[mM](?P<M>\d{1,2})$")
    df["date"] = pd.to_datetime(
        extracted["Y"].astype(int).astype(str) + "-" + extracted["M"].astype(int).astype(str).str.zfill(2),
        format="%Y-%m",
        errors="coerce",
    ).dt.tz_localize(None)
    if "coicop" in df.columns:
        df["coicop"] = df["coicop"].astype(str).str.strip().str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    df.sort_values(["geo_label", "coicop", "date"], inplace=True)
    return df.dropna(subset=["date"]).reset_index(drop=True)

hicp_data = load_hicp_data()

# ---------------------------------------------------
# 2. DEFINE RECIPES
# ---------------------------------------------------
recipes = {
    "Vanillekipferl": [
        {"ingredient": "Mehl", "quantity": 250, "unit": "g", "coicop": "CP01112"},
        {"ingredient": "Butter", "quantity": 200, "unit": "g", "coicop": "CP01151"},
        {"ingredient": "Zucker", "quantity": 70, "unit": "g", "coicop": "CP01181"},
        {"ingredient": "Mandeln", "quantity": 100, "unit": "g", "coicop": "CP01163"},
        {"ingredient": "Vanillezucker", "quantity": 10, "unit": "g", "coicop": "CP01192"},
    ],
    "Lebkuchen": [
        {"ingredient": "Mehl", "quantity": 250, "unit": "g", "coicop": "CP01112"},
        {"ingredient": "Honig", "quantity": 150, "unit": "g", "coicop": "CP01182"},
        {"ingredient": "Zucker", "quantity": 100, "unit": "g", "coicop": "CP01181"},
        {"ingredient": "Eier", "quantity": 2, "unit": "Stk", "coicop": "CP01147"},
        {"ingredient": "Gewürze", "quantity": 20, "unit": "g", "coicop": "CP01193"},
        {"ingredient": "Mandeln", "quantity": 50, "unit": "g", "coicop": "CP01163"},
    ],
    "Butterkekse": [
        {"ingredient": "Mehl", "quantity": 300, "unit": "g", "coicop": "CP01112"},
        {"ingredient": "Butter", "quantity": 200, "unit": "g", "coicop": "CP01151"},
        {"ingredient": "Zucker", "quantity": 100, "unit": "g", "coicop": "CP01181"},
        {"ingredient": "Eier", "quantity": 2, "unit": "Stk", "coicop": "CP01147"},
        {"ingredient": "Milch", "quantity": 50, "unit": "ml", "coicop": "CP01143"},
    ],
    "Zimtsterne": [
        {"ingredient": "Eiweiß", "quantity": 2, "unit": "Stk", "coicop": "CP01147"},
        {"ingredient": "Zucker", "quantity": 250, "unit": "g", "coicop": "CP01181"},
        {"ingredient": "Mandeln", "quantity": 200, "unit": "g", "coicop": "CP01163"},
        {"ingredient": "Zimt", "quantity": 5, "unit": "g", "coicop": "CP01192"},
    ],
    "Linzer Augen": [
        {"ingredient": "Mehl", "quantity": 300, "unit": "g", "coicop": "CP01112"},
        {"ingredient": "Butter", "quantity": 200, "unit": "g", "coicop": "CP01211"},
        {"ingredient": "Zucker", "quantity": 100, "unit": "g", "coicop": "CP01181"},
        {"ingredient": "Eier", "quantity": 1, "unit": "Stk", "coicop": "CP01143"},
        {"ingredient": "Gemahlene Nüsse", "quantity": 100, "unit": "g", "coicop": "CP01162"},
        {"ingredient": "Marmelade", "quantity": 100, "unit": "g", "coicop": "CP01182"},
    ],
}

# Expanded color palette for better distinction
COLOR_PALETTE = [
    "#e63946", "#2a9d8f", "#f4a261", "#264653", "#e76f51",
    "#06aed5", "#8338ec", "#ffbe0b", "#fb5607", "#3a86ff",
    "#ff006e", "#06ffa5", "#774936", "#c9184a", "#52b788", "#ffd60a",
]

# ---------------------------------------------------
# 3. SIDEBAR SELECTION
# ---------------------------------------------------
selected_recipe = st.sidebar.selectbox("Rezept auswählen", list(recipes.keys()))
selected_country = st.sidebar.selectbox("Land auswählen", sorted(hicp_data["geo_label"].unique()))

ingredients_df = pd.DataFrame(recipes[selected_recipe])

# ---------------------------------------------------
# 4. COMPUTE INDICES
# ---------------------------------------------------
def compute_recipe_index(df_ingr, hicp_data, country_label):
    df_country = hicp_data[hicp_data["geo_label"] == country_label].copy()
    value_col = next((c for c in ["y", "value", "values", "midx", "hicp", "index"] if c in df_country.columns), None)
    if value_col is None:
        return pd.DataFrame(columns=["date", "recipe_index"])
    df_country = df_country.rename(columns={value_col: "y"}) if value_col != "y" else df_country
    df = df_ingr.copy()
    df["weight"] = df["quantity"] / df["quantity"].sum()
    merged = df_country.merge(df, on="coicop", how="inner").dropna(subset=["date", "y"])
    if merged.empty:
        return pd.DataFrame(columns=["date", "recipe_index"])
    merged["date"] = pd.to_datetime(merged["date"]).dt.tz_localize(None)
    merged["y"] = pd.to_numeric(merged["y"], errors="coerce")
    merged["weighted"] = merged["y"] * merged["weight"]
    return (
        merged.groupby("date", as_index=False)["weighted"]
        .sum()
        .rename(columns={"weighted": "recipe_index"})
        .sort_values("date")
        .reset_index(drop=True)
    )

def get_ingredient_indices(df_ingr, hicp_data, country_label):
    df_country = hicp_data[hicp_data["geo_label"] == country_label].copy()
    value_col = next((c for c in ["y", "value", "values", "midx", "hicp", "index"] if c in df_country.columns), None)
    if value_col is None:
        return pd.DataFrame()
    df_country = df_country.rename(columns={value_col: "y"}) if value_col != "y" else df_country
    merged = df_country.merge(df_ingr[["ingredient", "coicop"]], on="coicop", how="inner").dropna(subset=["date", "y"])
    merged["date"] = pd.to_datetime(merged["date"]).dt.tz_localize(None)
    merged["y"] = pd.to_numeric(merged["y"], errors="coerce")
    return merged[["date", "ingredient", "y"]].sort_values("date").reset_index(drop=True)

recipe_index = compute_recipe_index(ingredients_df, hicp_data, selected_country)
ingredient_indices = get_ingredient_indices(ingredients_df, hicp_data, selected_country)

# Create color mapping for consistent colors across charts
ingredient_color_map = {ing: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, ing in enumerate(ingredients_df["ingredient"].unique())}

# ---------------------------------------------------
# 5. VISUALIZATIONS
# ---------------------------------------------------
# Create columns for pie chart and weighted price index chart (1:2 ratio)
col_pie, col_index = st.columns([1, 2])

with col_pie:
    st.subheader("🥣 Zutatenverhältnisse") # (circa eine Portion)
    fig_pie = px.pie(
        ingredients_df,
        values="quantity",
        names="ingredient",
        color="ingredient",
        color_discrete_map=ingredient_color_map,
    )
    fig_pie.update_traces(
        hovertemplate="<b>%{label}</b><br>Menge: %{value} %{customdata}<br>Anteil: %{percent}<extra></extra>",
        customdata=ingredients_df["unit"]
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_index:
    st.subheader("📈 Individuelle Zutaten-Preisindizes")
    if ingredient_indices.empty:
        st.warning("⚠️ Keine passende Zeitreihe für dieses Rezept und Land gefunden.")
    else:
        fig_multi = px.line(
            ingredient_indices,
            x="date",
            y="y",
            color="ingredient",
            labels={"y": "Preisinde (2015 = 100)", "date": "Jahr"},
            color_discrete_map=ingredient_color_map,
        )
        fig_multi.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Datum: %{x|%Y}<br>Preisindex: %{y:.2f}<extra></extra>"
        )
        fig_multi.update_xaxes(type="date", dtick="M12", tickformat="%Y")
        fig_multi.update_layout(
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            legend_title_text=""
        )
        st.plotly_chart(fig_multi, use_container_width=True)

# Now show the weighted recipe price index below the columns (full width)
st.subheader("📈 Gewichteter Preisindex")
if recipe_index.empty:
    st.warning("⚠️ Keine passende Zeitreihe für dieses Rezept und Land gefunden.")
else:
    # y_min/y_max computed but not used, kept for potential future bounds
    y_min = min(recipe_index["recipe_index"].min(), ingredient_indices["y"].min()) if not ingredient_indices.empty else recipe_index["recipe_index"].min()
    y_max = max(recipe_index["recipe_index"].max(), ingredient_indices["y"].max()) if not ingredient_indices.empty else recipe_index["recipe_index"].max()

    fig_line = px.line(
        recipe_index,
        x="date",
        y="recipe_index",
        labels={"recipe_index": "Rezept-Preisindex (2015 = 100)", "date": "Jahr"},
    )
    fig_line.update_traces(
        line_color="#c41e3a",
        line_width=3,
        hovertemplate="<b>%{x|%Y-%m}</b><br>Preisindex: %{y:.2f}<extra></extra>"
    )
    fig_line.update_xaxes(type="date", dtick="M12", tickformat="%Y")
    st.plotly_chart(fig_line, use_container_width=True)


### table for internal use only
#st.subheader("🧾 Zutaten (circa eine Portion)")
#st.dataframe(ingredients_df, hide_index=True, use_container_width=True)


# ---------------------------------------------------
# 6. FOOTER
# ---------------------------------------------------
st.markdown("---")
st.caption("WIFO-Dashboard. Quelle: Eurostat PRC_HICP_MIDX (COICOP 5-stelligen Preisindizes (2015 = 100).")
