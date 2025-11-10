import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config("🎄 Preis-Index Dashboard", layout="wide")

st.title("🍪 Wie teuer sind Weihnachtskekse? 🎅")
# 😭

# ---------------------------------------------------
# 1. LOAD EUROSTAT DATA
# ---------------------------------------------------
@st.cache_data
def load_hicp_data():
    df = pd.read_csv("prc_hicp_midx_clean.csv")
    s = df["date"].astype(str).str.strip()
    extracted = s.str.extract(r"^(?P<Y>\d{4})[mM](?P<M>\d{1,2})$")
    df["date"] = pd.to_datetime(
        extracted["Y"].astype(int).astype(str) + "-" + extracted["M"].astype(int).astype(str).str.zfill(2),
        format="%Y-%m",
        errors="coerce",
    )
    df = df.loc[~df["date"].isna()].copy()
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    if "coicop" in df.columns:
        df["coicop"] = df["coicop"].astype(str).str.strip().str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    if "geo_label" in df.columns:
        df["geo_label"] = df["geo_label"].astype(str).str.strip()
    df.sort_values(["geo_label", "coicop", "date"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

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
    #"Kokosmakronen": [
    #    {"ingredient": "Eiweiß", "quantity": 2, "unit": "Stk", "coicop": "CP01143"},
    #    {"ingredient": "Zucker", "quantity": 150, "unit": "g", "coicop": "CP01181"},
    #    {"ingredient": "Kokosraspeln", "quantity": 200, "unit": "g", "coicop": "CP01164"},
    #],
    "Linzer Augen": [
        {"ingredient": "Mehl", "quantity": 300, "unit": "g", "coicop": "CP01112"},
        {"ingredient": "Butter", "quantity": 200, "unit": "g", "coicop": "CP01211"},
        {"ingredient": "Zucker", "quantity": 100, "unit": "g", "coicop": "CP01181"},
        {"ingredient": "Eier", "quantity": 1, "unit": "Stk", "coicop": "CP01143"},
        {"ingredient": "Gemahlene Nüsse", "quantity": 100, "unit": "g", "coicop": "CP01162"},
        {"ingredient": "Marmelade", "quantity": 100, "unit": "g", "coicop": "CP01182"},
    ],
    #"Spitzbuben": [
    #    {"ingredient": "Mehl", "quantity": 300, "unit": "g", "coicop": "CP01112"},
    #    {"ingredient": "Butter", "quantity": 200, "unit": "g", "coicop": "CP01211"},
    #    {"ingredient": "Zucker", "quantity": 100, "unit": "g", "coicop": "CP01181"},
    #    {"ingredient": "Eier", "quantity": 1, "unit": "Stk", "coicop": "CP01143"},
    #    {"ingredient": "Mandeln", "quantity": 80, "unit": "g", "coicop": "CP01162"},
    #    {"ingredient": "Marmelade", "quantity": 100, "unit": "g", "coicop": "CP01182"},
    #],
    #"Rumkugeln": [
    #    {"ingredient": "Schokolade", "quantity": 200, "unit": "g", "coicop": "CP01185"},
    #    {"ingredient": "Butter", "quantity": 100, "unit": "g", "coicop": "CP01211"},
    #    {"ingredient": "Zucker", "quantity": 80, "unit": "g", "coicop": "CP01181"},
    #    {"ingredient": "Rum", "quantity": 20, "unit": "ml", "coicop": "CP02131"},
    #    {"ingredient": "Kakaopulver", "quantity": 30, "unit": "g", "coicop": "CP01185"},
    #    {"ingredient": "Kekskrümel", "quantity": 100, "unit": "g", "coicop": "CP01115"},
    #],
    #"Apfelkuchen": [
    #    {"ingredient": "Mehl", "quantity": 300, "unit": "g", "coicop": "CP01112"},
    #    {"ingredient": "Zucker", "quantity": 150, "unit": "g", "coicop": "CP01181"},
    #    {"ingredient": "Butter", "quantity": 150, "unit": "g", "coicop": "CP01211"},
    #    {"ingredient": "Eier", "quantity": 3, "unit": "Stk", "coicop": "CP01143"},
    #    {"ingredient": "Äpfel", "quantity": 400, "unit": "g", "coicop": "CP01171"},
    #    {"ingredient": "Milch", "quantity": 100, "unit": "ml", "coicop": "CP01141"},
    #    {"ingredient": "Backpulver", "quantity": 10, "unit": "g", "coicop": "CP01193"},
    #    {"ingredient": "Zimt", "quantity": 3, "unit": "g", "coicop": "CP01193"},
    #],
    #"Sachertorte": [
    #    {"ingredient": "Mehl", "quantity": 150, "unit": "g", "coicop": "CP01112"},
    #    {"ingredient": "Butter", "quantity": 150, "unit": "g", "coicop": "CP01211"},
    #    {"ingredient": "Zucker", "quantity": 150, "unit": "g", "coicop": "CP01181"},
    #    {"ingredient": "Eier", "quantity": 6, "unit": "Stk", "coicop": "CP01143"},
    #    {"ingredient": "Schokolade", "quantity": 200, "unit": "g", "coicop": "CP01185"},
    #    {"ingredient": "Aprikosenmarmelade", "quantity": 150, "unit": "g", "coicop": "CP01182"},
    #    {"ingredient": "Meersalz", "quantity": 2, "unit": "g", "coicop": "CP01193"},
    #],
    #"Käsekuchen": [
    #    {"ingredient": "Magerquark", "quantity": 500, "unit": "g", "coicop": "CP01142"},
    #    {"ingredient": "Zucker", "quantity": 150, "unit": "g", "coicop": "CP01181"},
    #    {"ingredient": "Butter", "quantity": 100, "unit": "g", "coicop": "CP01211"},
    #    {"ingredient": "Eier", "quantity": 3, "unit": "Stk", "coicop": "CP01143"},
    #    {"ingredient": "Mehl", "quantity": 200, "unit": "g", "coicop": "CP01112"},
    #    {"ingredient": "Milch", "quantity": 100, "unit": "ml", "coicop": "CP01141"},
    #    {"ingredient": "Vanillezucker", "quantity": 8, "unit": "g", "coicop": "CP01181"},
    #],
    #"Schwarzwälder Kirschtorte": [
    #    {"ingredient": "Mehl", "quantity": 150, "unit": "g", "coicop": "CP01112"},
    #    {"ingredient": "Zucker", "quantity": 150, "unit": "g", "coicop": "CP01181"},
    #    {"ingredient": "Butter", "quantity": 150, "unit": "g", "coicop": "CP01211"},
    #    {"ingredient": "Eier", "quantity": 5, "unit": "Stk", "coicop": "CP01143"},
    #    {"ingredient": "Kakaopulver", "quantity": 50, "unit": "g", "coicop": "CP01185"},
    #    {"ingredient": "Sahne", "quantity": 400, "unit": "ml", "coicop": "CP01144"},
    #    {"ingredient": "Kirschen", "quantity": 350, "unit": "g", "coicop": "CP01173"},
    #    {"ingredient": "Kirschwasser", "quantity": 50, "unit": "ml", "coicop": "CP02131"},
    #],
    #"Marmorkuchen": [
    #    {"ingredient": "Mehl", "quantity": 300, "unit": "g", "coicop": "CP01112"},
    #    {"ingredient": "Zucker", "quantity": 200, "unit": "g", "coicop": "CP01181"},
    #    {"ingredient": "Butter", "quantity": 200, "unit": "g", "coicop": "CP01211"},
    #    {"ingredient": "Eier", "quantity": 4, "unit": "Stk", "coicop": "CP01143"},
    #    {"ingredient": "Milch", "quantity": 100, "unit": "ml", "coicop": "CP01141"},
    #    {"ingredient": "Kakaopulver", "quantity": 30, "unit": "g", "coicop": "CP01185"},
    #    {"ingredient": "Backpulver", "quantity": 10, "unit": "g", "coicop": "CP01193"},
    #],
    #"Bienenstich": [
    #    {"ingredient": "Mehl", "quantity": 500, "unit": "g", "coicop": "CP01112"},
    #    {"ingredient": "Milch", "quantity": 250, "unit": "ml", "coicop": "CP01141"},
    #    {"ingredient": "Zucker", "quantity": 100, "unit": "g", "coicop": "CP01181"},
    #    {"ingredient": "Butter", "quantity": 100, "unit": "g", "coicop": "CP01211"},
    #    {"ingredient": "Eier", "quantity": 2, "unit": "Stk", "coicop": "CP01143"},
    #    {"ingredient": "Mandelblättchen", "quantity": 100, "unit": "g", "coicop": "CP01162"},
    #    {"ingredient": "Honig", "quantity": 50, "unit": "g", "coicop": "CP01182"},
    #    {"ingredient": "Vanillepuddingpulver", "quantity": 40, "unit": "g", "coicop": "CP01181"},
    #],
    #"Rüblikuchen": [
    #    {"ingredient": "Karotten", "quantity": 300, "unit": "g", "coicop": "CP01172"},
    #    {"ingredient": "Mehl", "quantity": 200, "unit": "g", "coicop": "CP01112"},
    #    {"ingredient": "Zucker", "quantity": 150, "unit": "g", "coicop": "CP01181"},
    #    {"ingredient": "Eier", "quantity": 4, "unit": "Stk", "coicop": "CP01143"},
    #    {"ingredient": "Mandeln", "quantity": 100, "unit": "g", "coicop": "CP01162"},
    #    {"ingredient": "Sonnenblumenöl", "quantity": 100, "unit": "ml", "coicop": "CP01212"},
    #    {"ingredient": "Backpulver", "quantity": 10, "unit": "g", "coicop": "CP01193"},
    #],
}

# Expanded color palette for better distinction
COLOR_PALETTE = [
    "#e63946",  # Red
    "#2a9d8f",  # Teal
    "#f4a261",  # Orange
    "#264653",  # Dark blue-green
    "#e76f51",  # Coral
    "#06aed5",  # Bright blue
    "#8338ec",  # Purple
    "#ffbe0b",  # Yellow
    "#fb5607",  # Burnt orange
    "#3a86ff",  # Blue
    "#ff006e",  # Hot pink
    "#06ffa5",  # Mint green
    "#774936",  # Brown
    "#c9184a",  # Dark pink
    "#52b788",  # Green
    "#ffd60a",  # Gold
]

# ---------------------------------------------------
# 3. SIDEBAR SELECTION
# ---------------------------------------------------
#st.sidebar.header("🎅 Konfiguration")
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
    if value_col != "y":
        df_country = df_country.rename(columns={value_col: "y"})
    df = df_ingr.copy()
    df["weight"] = df["quantity"] / df["quantity"].sum()
    df["coicop"] = df["coicop"].astype(str).str.strip().str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    merged = df_country.merge(df, on="coicop", how="inner")
    if merged.empty:
        return pd.DataFrame(columns=["date", "recipe_index"])
    merged = merged.loc[~merged["date"].isna()].copy()
    merged["date"] = pd.to_datetime(merged["date"]).dt.tz_localize(None)
    merged["y"] = pd.to_numeric(merged["y"], errors="coerce")
    merged = merged.dropna(subset=["y"])
    if merged.empty:
        return pd.DataFrame(columns=["date", "recipe_index"])
    merged["weighted"] = merged["y"] * merged["weight"]
    recipe_index = (
        merged.groupby("date", as_index=False)["weighted"]
        .sum()
        .rename(columns={"weighted": "recipe_index"})
        .sort_values("date")
        .reset_index(drop=True)
    )
    return recipe_index

def get_ingredient_indices(df_ingr, hicp_data, country_label):
    df_country = hicp_data[hicp_data["geo_label"] == country_label].copy()
    value_col = next((c for c in ["y", "value", "values", "midx", "hicp", "index"] if c in df_country.columns), None)
    if value_col is None:
        return pd.DataFrame()
    if value_col != "y":
        df_country = df_country.rename(columns={value_col: "y"})
    df = df_ingr.copy()
    df["coicop"] = df["coicop"].astype(str).str.strip().str.upper().str.replace(r"[^A-Z0-9]", "", regex=True)
    merged = df_country.merge(df[["ingredient", "coicop"]], on="coicop", how="inner")
    if merged.empty:
        return pd.DataFrame()
    merged = merged.loc[~merged["date"].isna()].copy()
    merged["date"] = pd.to_datetime(merged["date"]).dt.tz_localize(None)
    merged["y"] = pd.to_numeric(merged["y"], errors="coerce")
    merged = merged.dropna(subset=["y"])
    return merged[["date", "ingredient", "y"]].sort_values("date").reset_index(drop=True)

recipe_index = compute_recipe_index(ingredients_df, hicp_data, selected_country)
ingredient_indices = get_ingredient_indices(ingredients_df, hicp_data, selected_country)

# Create color mapping for consistent colors across charts
ingredient_color_map = {ing: COLOR_PALETTE[i % len(COLOR_PALETTE)] for i, ing in enumerate(ingredients_df["ingredient"].unique())}

# ---------------------------------------------------
# 5. VISUALIZATIONS
# ---------------------------------------------------
st.subheader("🥣 Zutatenverhältnisse")
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

st.subheader("📈 Gewichteter Preisindex")
if recipe_index.empty:
    st.warning("⚠️ Keine passende Zeitreihe für dieses Rezept und Land gefunden.")
else:
    # Calculate combined min/max for consistent y-axis across both charts
    y_min = recipe_index["recipe_index"].min()
    y_max = recipe_index["recipe_index"].max()
    if not ingredient_indices.empty:
        y_min = min(y_min, ingredient_indices["y"].min())
        y_max = max(y_max, ingredient_indices["y"].max())
    #y_range = [y_min * 0.95, y_max * 1.05]
    
    fig_line = px.line(
        recipe_index,
        x="date",
        y="recipe_index",
        labels={"recipe_index": "Rezept-Preisindex", "date": "Jahr"},
    )
    fig_line.update_traces(
        line_color="#c41e3a",
        line_width=3,
        hovertemplate="<b>%{x|%Y-%m}</b><br>Preisindex: %{y:.2f}<extra></extra>"
    )
    fig_line.update_xaxes(type="date", dtick="M12", tickformat="%Y")
    #fig_line.update_yaxes(range=y_range)
    st.plotly_chart(fig_line, use_container_width=True)

if not ingredient_indices.empty:
    fig_multi = px.line(
        ingredient_indices,
        x="date",
        y="y",
        color="ingredient",
        title="Individuelle Zutaten-Preisindizes",
        labels={"y": "Preisindex", "date": "Jahr", "ingredient": "Zutat"},
        color_discrete_map=ingredient_color_map,
    )
    fig_multi.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Datum: %{x|%Y-%m}<br>Preisindex: %{y:.2f}<extra></extra>"
    )
    fig_multi.update_xaxes(type="date", dtick="M12", tickformat="%Y")
    #fig_multi.update_yaxes(range=y_range)
    fig_multi.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
    st.plotly_chart(fig_multi, use_container_width=True)

st.subheader("🧾 Zutaten (circa eine Portion)")
st.dataframe(ingredients_df, hide_index=True, use_container_width=True)

# ---------------------------------------------------
# 6. FOOTER
# ---------------------------------------------------
st.markdown("---")
st.caption("🎄 Prototyp-Dashboard — Eurostat COICOP 5-stelligen Preisindizes (PRC_HICP_MIDX). 2015 = 100.")
