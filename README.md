# Learning Path Generator with Model Context Protocol (MCP)

This project is a Streamlit-based web application that generates personalized learning paths using the Model Context Protocol (MCP). It integrates with various services including YouTube, Google Drive, and Notion to create comprehensive learning experiences.

## Features

- 🎯 Generate personalized learning paths based on your goals
- 🎥 Integration with YouTube for video content
- 📁 Google Drive integration for document storage
- 📝 Notion integration for note-taking and organization
- 🚀 Real-time progress tracking
- 🎨 User-friendly Streamlit interface
- 🔐 **NEW**: Secure user authentication and account management
- 💾 **NEW**: Automatic saving of learning paths and interview sessions
- 👤 **NEW**: User profiles with progress history
- 🎯 **NEW**: Mock interview sessions with AI evaluation
- 🎤 **NEW**: Voice assistant for hands-free interaction

## Prerequisites

- Python 3.10+
- Google ai Studio API Key
- Pipedream URLs for integrations (YouTube and either Drive or Notion)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mcpLearningPath
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python init_database.py
```

5. (Optional) Test the authentication system:
```bash
python test_auth.py
```

## Configuration

Before running the application, you'll need to set up:

1. Google API Key
2. Pipedream URLs for:
   - YouTube (required)
   - Google Drive or Notion (based on your preference)

## Running the Application

To start the application, run:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501` by default.

## Usage

### Getting Started
1. **Register an Account**: Click "Register" in the sidebar to create your account
2. **Login**: Use your credentials to login and access all features
3. **Configure APIs**: Enter your Google AI Studio API key and Pipedream URLs in the sidebar

### Learning Path Generator
1. Select your preferred secondary tool (Drive or Notion)
2. Enter your learning goal (e.g., "I want to learn python basics in 3 days")
3. Click "Generate Learning Path" to create your personalized learning plan
4. Your learning paths are automatically saved to your profile

### Mock Interview Simulator
1. Configure interview settings (type, role, language, difficulty)
2. Fill in your candidate profile for personalized questions
3. Take the pre-test to unlock live interview features
4. Complete the interview with AI evaluation and feedback
5. View your final report and recommendations
6. All interview sessions are saved to your profile

### Voice Assistant
1. Enable voice mode in the interview section
2. Use voice commands like "start interview", "next question", "repeat question"
3. Get hands-free interview experience with text-to-speech feedback

## Project Structure

- `app.py` - Main Streamlit application with authentication integration
- `auth.py` - Authentication system and user management
- `utils.py` - Utility functions and helper methods
- `mock_interview.py` - Mock interview system with AI evaluation
- `voice_assistant.py` - Voice assistant with three-stage processing
- `prompt.py` - Prompt template
- `requirements.txt` - Project dependencies
- `init_database.py` - Database initialization script
- `test_auth.py` - Authentication system test suite
- `AUTHENTICATION_GUIDE.md` - Detailed authentication documentation
- `users.db` - SQLite database (created after initialization)

## Database Schema

The application uses SQLite with the following main tables:
- **users** - User accounts and authentication data
- **user_sessions** - Login sessions and tokens
- **learning_progress** - Saved learning paths and progress
- **interview_sessions** - Mock interview results and reports
- **user_preferences** - User-specific application settings

See `AUTHENTICATION_GUIDE.md` for detailed database documentation.

## Security Features

- 🔐 Secure password hashing with PBKDF2 and random salts
- 🎫 Token-based session management with expiration
- ✅ Input validation and SQL injection prevention
- 🧹 Automatic cleanup of expired sessions
- 📧 Email format validation
- 💪 Strong password requirements enforcement




## Complete Tutorial: How to Connect MCP Server to Cursor

## Prerequisites & Setup

## **Step 1: Install Node.js( ignore if already installed)**

Before we begin, you need Node.js installed on your computer to run the setup commands.

**For Windows Users:**

1. **Open your web browser** and navigate to: `https://nodejs.org`
2. **Download the LTS version** (Long Term Support) - it will show something like "18.17.0 LTS"
3. **Run the downloaded .msi file**
4. **Follow the installation wizard**:
    - Accept the license agreement
    - Keep the default installation path
    - **Important**: Make sure "Add to PATH" is checked
    - **Important**: Check "Automatically install the necessary tools" when prompted
5. **Restart your computer** after installation
6. **Verify installation**: Open Command Prompt or PowerShell and type:
    
    `textnode --version`
    `npm --version`
    
    You should see version numbers for both commands.
    

**For Mac Users:**

1. Visit `https://nodejs.org` and download the LTS version
2. Run the downloaded .pkg file and follow the installer
3. Verify installation in Terminal with `node --version`

**For Linux Users:**

1. Use your package manager or download from nodejs.org
2. Verify with `node --version` in terminal
## **Step 2: Ensure Cursor is Installed (ignore if already installed)**

Make sure you have Cursor IDE installed on your computer. If not:

1. Visit `https://cursor.sh`
2. Download and install Cursor for your operating system
3. Launch Cursor to ensure it's working properly

## Accessing Composio MCP Platform

## **Step 3: Navigate to Composio MCP**

1. **Open your web browser**
2. **Navigate to**: `https://mcp.composio.dev`
3. You'll see the Composio MCP homepage with various integration options

## **Step 4: Search for LinkedIn Integration**

1. **Look for the search bar** at the top of the page
2. **Type "LinkedIn"** in the search box
3. **Press Enter** or click the search icon
4. You should see LinkedIn appear under **"Marketing & social media"** category with description: *"LinkedIn is a professional networking platform enabling job seekers, companies, and thought..."*

## **Step 5: Access LinkedIn Integration**

1. **Click on the LinkedIn card/option**
2. You'll see two buttons: **"View Servers"** and **"Create Server"**
3. **Click "Create Server"** to begin the setup process

## Creating LinkedIn MCP Server

## **Step 6: Server Name Configuration**

1. A dialog box **"Create MCP Server"** will appear
2. **Enter a server name** in the "Server Name" field
    - Example: `LinkedIn-wp90c4` or `my-linkedin-server`
    - You'll see a green "Valid server name" message when it's acceptable
3. **Click "Next"** to proceed
## **Step 7: LinkedIn Authentication**

1. A **LinkedIn login page** will appear in a new tab/window
2. **Enter your LinkedIn credentials**:
    - Email or Phone number
    - Password
3. **Click "Sign in"**
4. **Complete any security verification** if prompted by LinkedIn
5. **Grant permissions** when LinkedIn asks for authorization

**Important**

 **Security Note**: This uses OAuth 2.0, so your password is not stored - only a secure token is created.
 ## Authentication & Configuration

**Step 8: Integration Confirmation**

After successful login, you'll see:

1. **"Integration Already Active"** message with a green checkmark ✅
2. This confirms your LinkedIn account is properly connected
3. **Click "Continue to Action Setup"**
## **Step 9: Configure LinkedIn Actions**

You'll see **"Configure Actions for LinkedIn"** with available options:

**Recommended Actions to Enable:**

- ☑️ **Create a LinkedIn post** - For posting content directly from Cursor
- ☑️ **Get company info** - For researching companies
- ☑️ **Get my info** - For accessing your profile data
- ☑️ **Delete LinkedIn Post** - For content management (optional)

**Instructions:**

1. **Check the boxes** for actions you want to enable
2. You can see the count at the top (e.g., "Selected Actions: 4/30")
3. **Click "Create Server"** when satisfied with your selection
## **Step 10: Get Your Setup Command**

After creating the server, you'll see:

1. **"MCP Server Created"** with green checkmark ✅
2. **"Choose your client and copy the setup command:"**
3. **Make sure "Cursor" tab is selected**
4. **Copy the command** that appears in the blue box - it will look like:
    
    `textnpx @composio/mcp@latest setup "https://mcp.composio.dev/composio/server/[your-unique-id]/mcp?include_composio_helper_actions=true&agent=cursor" "Testing" --client cursor`
    
5. **Copy this entire command** - you'll need it in the next step
## Terminal Setup Commands

## **Step 11: Run the Setup Command**

1. **Open your terminal/command prompt**:
    - **Windows**: Press `Win + R`, type `cmd`, press Enter
    - **Mac**: Press `Cmd + Space`, type "Terminal", press Enter
    - **Linux**: Use your preferred terminal application
2. **Navigate to any directory** (location doesn't matter for this command)
3. **Paste and run your copied command**:
    
    `bashnpx @composio/mcp@latest setup "https://mcp.composio.dev/composio/server/[your-unique-id]/mcp?include_composio_helper_actions=true&agent=cursor" "Testing" --client cursor`
    
4. **Press Enter** and wait for the process to complete
5. **Expected output**: You should see messages indicating successful setup and configuration file creation

**What this command does:**

- Downloads the Composio MCP package temporarily
- Sets up the LinkedIn server connection
- Configures it specifically for Cursor
- Creates necessary configuration files automatically

## Cursor Integration

## **Step 12: Access Cursor MCP Settings**

## **Step 12: Access Cursor MCP Settings**

1. **Open Cursor IDE**
2. **Open Command Palette**: Press `Ctrl + Shift + P` (Windows/Linux) or `Cmd + Shift + P` (Mac)
3. **Type "Cursor Settings"** and select it from the dropdown
4. **Look for "MCP" or "Tools & Integrations"** in the left sidebar
5. **Click on the MCP section**

## **Step 13: Verify LinkedIn Server**

In the MCP Tools section, you should see:

- **Your server name** (e.g., "Testing")
- **Green dot indicator** showing it's active and connected
- **Available actions** listed, including:
    - `LINKEDIN_CREATE_LINKED_IN_POST`
    - `LINKEDIN_GET_COMPANY_INFO`
    - `LINKEDIN_GET_MY_INFO`
    - `COMPOSIO_SEARCH_TOOLS`
    - And other helper functions

## **Step 14: Configuration File Verification**

The setup automatically creates a configuration file at:

- **Global**: `~/.cursor/mcp.json`
- **Project-specific**: `.cursor/mcp.json` in your project folder

The file should contain something like:

`json{
  "mcpServers": {
    "Testing": {
      "url": "https://mcp.composio.dev/composio/server/[your-id]/mcp?include_composio_helper_actions=true&agent=cursor"
    }
  }
}`

## Testing Your Integration

## **Step 15: Test Basic Functionality**

1. **Open Cursor's AI Chat**: Press `Ctrl + I` (Windows/Linux) or `Cmd + I` (Mac)
2. **Try these test commands**:

**Test 1 - Get Your Profile:**

`textGet my LinkedIn profile information`

**Test 2 - Company Research:**

`textGet company information for Google`

**Test 3 - Create a Post (be careful with this one):**

`textCreate a LinkedIn post about learning AI development with the text "Excited to be learning AI development! #AI #Development"`

1. **Accept tool usage** when Cursor prompts you to allow MCP tool execution
2. **Verify responses** - you should get actual data from your LinkedIn account

**That’s it—you nailed it! Wishing you all the best!**
