# Real Estate Investment AI Dashboard 🏙️

## Overview
This project is an end-to-end data science and geospatial analytics application designed to evaluate real estate investment opportunities. It processes raw lease-up data, categorizes properties using unsupervised machine learning, and presents the findings through a deployed interactive dashboard featuring a natural language AI assistant.

## Architecture & Features
* **Data Engineering & EDA:** Automated cleaning of raw property data, handling missing geographic coordinates, and engineering key performance metrics (Lease-Up Time, Rent Premiums).
* **Machine Learning (Clustering):** Applied K-Means clustering to segment properties into distinct investment archetypes (e.g., Suburban High-Velocity, Urban Luxury High-Rise) based on yield and performance metrics.
* **Interactive Geospatial Dashboard:** Built with Streamlit, allowing users to filter properties by investment strategy and dynamically jump to specific buildings on an interactive map.
* **AI Chat Assistant (LLM Integration):** Integrated Meta's Llama 3.1 (8B) model via the Groq Cloud API. The application utilizes prompt engineering and a "RAG-lite" context injection approach to allow users to ask natural language questions about the property data without the risk of hallucination.

## Live Application
The dashboard is currently deployed on Streamlit Community Cloud: 
[Insert your Streamlit App Link Here]

## Technologies Used
* **Python** (Pandas, Scikit-Learn)
* **Streamlit** (Web framework, session state management, cloud deployment)
* **Groq API** (Ultra-low latency LLM inference)
* **Meta Llama 3.1 8B** (Natural Language Processing)
