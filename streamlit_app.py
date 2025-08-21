import streamlit as st
import openai

st.title('LoL Chat Bot For Item Builds')

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
# if prompt := st.chat_input("Hey, What's up?"):
#     # Display user message in chat message container
#     st.chat_message("user").markdown(prompt)
#     # Add user message to chat history
#     st.session_state.messages.append({"role": "user", "content": prompt})
    
#     response = f"Echo: {prompt}"
#     # Display assistant response in chat message container
#     with st.chat_message("assistant"):
#         st.markdown(response)
#     # Add assistant response to chat history
#     st.session_state.messages.append({"role": "assistant", "content": response})

openai.api_key = st.secrets["OPENAI_API_KEY"]

def build_prompt(champion, role, enemy_champ):
    base_prompt = f"""
    You are a League of Legends coach AI specializing in item builds and matchup advice for Summoner's Rift 5v5 game mode.
    
    Here are a few examples:
    
    Champion: Ahri  
    Role: Mid  
    Enemy: Zed   
    Advice: Start with Doran's Ring and two pots. Build into Malignance first for lower ult cooldown or consider building Zhonya's Hourglass first to avoid Zed's burst.
    Build Sorcerer's Boots second. Build Malignance or Zhonya's third depending on what you bought first. Follow this with items like Shadowflame, Rabadon's Deathcap, or even Mejai's Soulstealer for more damage.
    
    Champion: Miss Fortune  
    Role: ADC  
    Enemy: Jinx   
    Advice: Start Doran's Blade and one pot. Build into Youmuu's Ghostblade first which is strong due to early lethality and movespeed. However, also consider Bloodthirster first to negate Jinx's long range poke. Build Boots of Swiftness
    second. Typically build crit items like The Collector, Infinity Edge (necessary), Lord Dominik's Regards, or even Essence Reaver. Edge of Night and Bloodthirster (if not bought first) provide survivability late game.
    
    Champion: Malphite  
    Role: Top
    Enemy: Kennen   
    Advice: Start Doran's Ring for stronger poke with Malphite's Q and two pots. Build into Malignance first which will provide kill pressure on Kennen who is a squisky target. Buy Mercury's Treads next and even consider buying Null-Magic Mantle
    for MR before finishing Malignance. Build Hallow Radiance next for even more protection against Kennen's burst. Finally, build into common tank items like Frozen Heart, Kaenic Rookern, Jak'Sho, Thornmail, or Unending Despair.
    
    
    ---
    
    Champion: {champion}
    Role: {role}
    Enemy: {enemy_champ}
    Advice:
    """
    return base_prompt.strip()

def get_build_advice(champion, role, enemy_champ):
    prompt = build_prompt(champion, role, enemy_champ)
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant and League of Legends coach."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=120
    )

    return response['choices'][0]['message']['content']
    # print(response.output_text)

champion = st.text_input("Your Champion", "Darius")
role = st.selectbox("Role", ["Top", "Jungle", "Mid", "ADC", "Support"])
enemy = st.text_input("Enemy Champion", "Teemo")

if st.button("Get Advice"):
    advice = get_build_advice(champion, role, enemy)
    st.markdown("### Advice:")
    st.write(advice)
