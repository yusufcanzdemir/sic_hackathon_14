# Feed-to-Life (Scrolling Archaeology)

Samsung Innovation Campus Generative AI Hackathon Project

Feed-to-Life is a web application focusing on the issue of digital addiction and digital well-being. Instead of restricting screen time or imposing rigid detox programs, this project reads the content users save or like not as mere "consumption," but as "proof of an unmet need." With the support of Artificial Intelligence, it suggests a single, constructive, offline micro-action to fulfill this need in the real world.

## The Core Philosophy and Workflow

The primary goal is not to suggest more content for the user to consume, but to transform the interest generated in front of the screen into a small, actionable event in real life. 

The application follows a structured pipeline:
1. User Data Input: The user uploads their exported social media history (synthetic JSON data is used for demonstration).
2. Data Analysis: The system analyzes viewing times, dominant categories, and behavioral flags (e.g., late-night usage patterns, narrow account loops).
3. Common Interest Detection: Identifying the core themes the user is interested in (e.g., recipes, music, outdoor travel).
4. AI Intervention: The system filters recommendations based on user-defined constraints (social environment and budget).
5. Offline Micro-Action: A specific, non-judgmental action is proposed.
6. Habit Building: A 21-day roadmap is generated to help the user slowly replace screen time with the new offline hobby.

## Key Features

* Comprehensive Dashboard: View summaries of total content consumed, peak active hours, and a category distribution chart built with Plotly.
* Personalized Preference Filters: Users can specify whether they want to do the activity alone, with family, or with friends, as well as set a specific budget limit.
* Gemini AI Integration: Uses Google Gemini models to provide empathetic, context-aware coaching without diagnosing or shaming the user.
* Memory and Revision: If the user rejects the AI's first suggestion, the AI recalls the feedback and generates a revised action.
* 21-Day Roadmap Generator: Breaks down the offline action into a three-phase calendar (Awareness, Limitation, New Habit) with daily progressive tracking.

## Project Structure

The repository is organized to maintain a clear separation between the user interface, artificial intelligence logic, and data processing.

* app.py: The main Streamlit application file containing the user interface and frontend logic.
* requirements.txt: The list of Python dependencies required to run the project.
* data/: Directory containing the synthetic data generated for the hackathon (profile.json, signals.json).
* ai/: Directory holding the AI pipeline.
  * api.py: Manages API calls to Google Gemini.
  * prompts.py: Contains the strict system prompts and safety rules for the AI.
  * ai.py: Contains fallback classification systems and local AI (Ollama) integration scripts.
* .streamlit/style.css: Custom CSS to enhance the application's appearance with a clean, neumorphic design.

## Installation and Setup

Follow these steps to run the project locally on your machine.

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/yusufcanzdemir/sic_hackathon_14
   cd sic_hackathon_14
   ```

2. Create a virtual environment to manage dependencies:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   * Windows (Command Prompt): `venv\Scripts\activate`
   * Windows (PowerShell): `venv\Scripts\Activate.ps1`
   * macOS / Linux: `source venv/bin/activate`

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   Create a `.env` file in the root directory. You will need a Google Gemini API key to run the core AI features.
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

6. Run the application:
   ```bash
   streamlit run app.py
   ```

7. When you are finished, you can close the virtual environment by typing:
   ```bash
   deactivate
   ```

## Team Workflow and Git Guidelines

To prevent merge conflicts during development, all team members must work on their respective branches:
* main: Only approved, working code resides here. Direct pushes to main are strictly prohibited.
* feature/ui: Branch for Streamlit UI development.
* feature/data: Branch for data manipulation, mock JSON generation, and backend logic.
* feature/ai: Branch for prompt management and API calls.

When a feature is complete, developers must push to their branch and open a Pull Request (PR) for code review before merging into the main branch.
