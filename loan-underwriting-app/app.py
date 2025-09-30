import streamlit as st

# Ultra-minimal test version
st.title("🏦 Test App - Databricks Apps")
st.write("If you see this, the basic app is working!")
st.success("✅ Streamlit started successfully")

# Test basic functionality
name = st.text_input("Enter your name:", value="Test User")
if st.button("Say Hello"):
    st.balloons()
    st.write(f"Hello, {name}! 👋")

st.info("This is an ultra-minimal version to test if Databricks Apps is working")