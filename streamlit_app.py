import streamlit as st
from openai import OpenAI
import pandas as pd
import numpy as np
import luadata

st.title('LoL Item Build AI Advisor with AI')

# Set OpenAI API key from Streamlit secrets
# openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set a default model
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

left, middle, right = st.columns(3, vertical_alignment="bottom")

def build_prompt(champion, role, enemy_champ):
    base_prompt = f"""
    You are a League of Legends coach AI specializing in item builds and matchup advice for Summoner's Rift 5v5 game mode. Only recommend items from the list below:
    
    Available Items: {lol_item_list}
    
    Here are a few examples:
    
    Prompt:
    Champion: Ahri  
    Role: Mid  
    Enemy: Zed
    
    Advice:
    Starting Items: Doran's Ring and two Health Potions.
    First Item: Build into Malignance first for lower ult cooldown or consider building Zhonya's Hourglass first to avoid Zed's burst.
    Other Items: Build Sorcerer's Boots second. Build Malignance or Zhonya's Hourglass third depending on what you bought first. Follow this with items like Shadowflame, Rabadon's Deathcap, or even Mejai's Soulstealer for more damage.
    Tips: Stay behind minions to shield against her Charm spell. Attempt to bait out her Charm before engaging yourself.
    
    Prompt:
    Champion: Miss Fortune  
    Role: ADC  
    Enemy: Jinx
    
    Advice:
    Starting Items: Doran's Blade and Health Potion.
    First Item: Youmuu's Ghostblade is strong due to early lethality and movespeed. However, also consider Bloodthirster first to negate Jinx's long range poke.
    Other Items: Build Boots of Swiftness second to help dodge Jinx's skill shots. Typically build crit items like Infinity Edge, The Collector, Lord Dominik's Regards, or even Essence Reaver. Edge of Night and Bloodthirster provide survivability late game.
    Tips: Be sure to use your Q spell on back line minions which can bounce and hit enemy champions. Take advatage of Jinx's E spell cooldown to engange on her.
    
    Prompt:
    Champion: Malphite  
    Role: Top
    Enemy: Kennen 
    
    Advice:
    Starting Items: Doran's Ring for stronger poke with Malphite's Q and two Health Potions.
    First Item: Malignance provides kill pressure on Kennen who is a squisky target.
    Other Items: Buy Mercury's Treads next for MR and to reduce Kenne's stun duration. Build Hallow Radiance next for even more protection against Kennen's burst. Finally, build into common tank items like Frozen Heart, Kaenic Rookern, Jak'Sho, Thornmail, or Unending Despair.
    Tips: Kennen has high mobility with Lightning Rush, bait this out before engaging so he can't escape. 
    
    
    ---
    
    Prompt:
    Champion: {champion}
    Role: {role}
    Enemy: {enemy_champ}
    
    Advice:
    """
    return base_prompt.strip()

def get_build_advice(champion, role, enemy_champ):
    prompt = build_prompt(champion, role, enemy_champ)

    response = client.chat.completions.create(
        model=st.session_state["openai_model"],
        messages=[
            {"role": "system", "content": "You are a helpful assistant and League of Legends coach."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=200,
        stream=True
    )

    return response

lol_champs = pd.read_csv("080725_LoL_champion_data_revised.csv", index_col=0)
champ_list = lol_champs["apiname"].to_list()

champion = left.selectbox("Your Champion", champ_list)
role = middle.selectbox("Role", ["Top", "Jungle", "Mid", "ADC", "Support"])
champ_list.remove(champion)
enemy = right.selectbox("Enemy Champion", champ_list)

data = luadata.read("lol_items.lua", encoding="utf-8")
lol_item_list = pd.DataFrame(data)
lol_item_list = lol_item_list.T
lol_item_list = lol_item_list[lol_item_list["type"].notnull()]
lol_item_list = lol_item_list.drop(["Muramana", "Fimbulwinter"])
normalized_data = pd.json_normalize(lol_item_list['modes'])
normalized_data.index = lol_item_list.index
lol_item_list = pd.concat([lol_item_list.drop(columns=['modes']), normalized_data], axis=1)
lol_item_list = lol_item_list[lol_item_list["classic sr 5v5"]]
lol_item_list = lol_item_list[lol_item_list["type"].apply(lambda x: "Legendary" in x or "Boots" in x or "Starter" in x or "Potion" in x or "Potion" in x)]
lol_item_list = ", ".join(lol_item_list.index.tolist())

if middle.button("Get Advice"):
    advice = get_build_advice(champion, role, enemy)
    middle.markdown("### Advice:")
    middle.write_stream(advice)
