# 🔬 Skinalyze - AI-Powered Skin Analysis Platform

A modern, beautiful web application for skin disease detection using artificial intelligence, built with Streamlit.

## ✨ Features

### 🔍 **AI Image Analysis**
- Upload skin images for instant AI-powered disease detection
- High accuracy analysis with confidence scores
- Support for JPG, JPEG, and PNG formats
- Detailed prediction results with visual feedback

### 💬 **Smart Medical Chatbot**
- Interactive symptom analysis
- Personalized medical guidance
- Comprehensive symptom tracking
- Professional medical recommendations

### 👤 **User Management**
- Secure user registration and authentication
- Password hashing with bcrypt
- Personal dashboard with analysis history
- User profile management

### 📊 **Dashboard & Analytics**
- Personal analysis history tracking
- User statistics and metrics
- Community user overview
- Real-time progress indicators

### 🎨 **Modern UI/UX**
- Beautiful gradient designs
- Responsive layout
- Interactive components
- Professional medical theme
- Mobile-friendly interface

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd skinalyze
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the app**
   Open your browser and navigate to `http://localhost:8501`

## 📦 Dependencies

- **streamlit** - Web application framework
- **sqlite3** - Database management
- **bcrypt** - Password hashing
- **gradio-client** - AI model integration
- **Pillow** - Image processing
- **plotly** - Interactive visualizations
- **pandas** - Data manipulation

## 🏗️ Project Structure

```
skinalyze/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
├── database.db        # SQLite database (auto-created)
└── temp/              # Temporary image storage (auto-created)
```

## 🔧 Configuration

The application uses SQLite database for user management and stores temporary images in the `temp/` directory. Both are created automatically when the app runs for the first time.

## 🎯 Usage

### 1. **Registration & Login**
- Create a new account or login with existing credentials
- Secure password hashing ensures data protection

### 2. **Image Analysis**
- Navigate to "Image Analysis" page
- Upload a clear image of the skin area
- Click "Analyze Image" for AI-powered detection
- View detailed results with confidence scores

### 3. **Medical Chatbot**
- Access the "AI Chatbot" page
- Fill in symptom information
- Receive personalized medical guidance
- Get professional recommendations

### 4. **Dashboard**
- View your analysis history
- Track personal statistics
- Access quick actions
- Monitor account information

## ⚠️ Medical Disclaimer

This application is for informational purposes only and should not replace professional medical advice. Always consult with a healthcare professional for proper diagnosis and treatment.

## 🔒 Privacy & Security

- User passwords are securely hashed using bcrypt
- Personal data is stored locally in SQLite database
- Images are temporarily processed and automatically deleted
- No personal medical information is shared with third parties

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support or questions:
- Email: support@skinalyze.com
- Create an issue in the repository
- Check the documentation

---

**Made with ❤️ using Streamlit**

🔬 **Skinalyze** - Revolutionizing skin health through AI-powered analysis