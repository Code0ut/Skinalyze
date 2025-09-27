# 🩺 Arogya Sahayak & Skinalyze - Complete Health Assistant Platform

A comprehensive, multilingual health analysis platform combining skin disease detection, general disease prediction, and maternal health risk assessment using artificial intelligence, built with Streamlit.

## ✨ Features

### 👩‍⚕️ **Maternal Health Risk Assessment**
- Vital signs analysis for maternal health risk prediction
- Input patient data: Age, Blood Pressure, Blood Sugar, Temperature, Heart Rate
- Risk categorization: Low, Medium, High
- Ideal for health workers in rural areas
- Multilingual support for better accessibility

### 🩺 **General Disease Prediction**
- Symptom-based disease prediction using AI
- Multi-symptom selection interface
- Preliminary diagnosis suggestions
- Comprehensive symptom database
- Medical disclaimers and safety recommendations

### 🔍 **AI Skin Analysis**
- Upload skin images for instant AI-powered disease detection
- High accuracy analysis with confidence scores
- Support for JPG, JPEG, and PNG formats
- Detailed prediction results with visual feedback

### 💬 **Smart Medical Chatbot**
- Interactive symptom analysis
- Personalized medical guidance
- Comprehensive symptom tracking
- Professional medical recommendations

### 🌐 **Multilingual Support**
- Available in English, Hindi (हिन्दी), and Marathi (मराठी)
- Complete interface translation
- Rural area accessibility focus
- Language persistence across sessions

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
- **joblib** - Model serialization
- **scikit-learn** - Machine learning models

## 🏗️ Project Structure

```
health-assistant/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── README.md          # Project documentation
├── database.db        # SQLite database (auto-created)
├── temp/              # Temporary image storage (auto-created)
├── model/             # ML model files directory
│   ├── maternal_risk_model.joblib      # Maternal health model
│   ├── disease_model.joblib            # Disease prediction model
│   ├── disease_label_encoder.joblib    # Disease label encoder
│   └── README.md                       # Model documentation
└── database/          # Training data directory
    ├── Training.csv                    # Symptom-disease dataset
    └── README.md                       # Data documentation
```

## 🔧 Configuration

The application uses SQLite database for user management and stores temporary images in the `temp/` directory. Both are created automatically when the app runs for the first time.

## 🎯 Usage

### 1. **Language Selection**
- Choose your preferred language from the sidebar
- Available: English, Hindi (हिन्दी), Marathi (मराठी)
- Language preference persists throughout the session

### 2. **Registration & Login**
- Create a new account or login with existing credentials
- Secure password hashing ensures data protection

### 3. **Maternal Health Risk Assessment**
- Navigate to "Maternal Health Risk" page
- Enter patient vitals (Age, BP, Blood Sugar, Temperature, Heart Rate)
- Click "Assess Risk Level" for AI-powered risk analysis
- View risk categorization and recommendations

### 4. **Disease Prediction**
- Access the "Disease Prediction" page
- Select multiple symptoms from the comprehensive list
- Click "Predict Disease" for preliminary diagnosis
- Review AI predictions with medical disclaimers

### 5. **Skin Analysis**
- Navigate to "Skin Analysis" page
- Upload a clear image of the skin area
- Click "Analyze Image" for AI-powered detection
- View detailed results with confidence scores

### 6. **Medical Chatbot**
- Access the "Medical Chatbot" page
- Fill in comprehensive symptom information
- Receive personalized medical guidance
- Get professional recommendations

### 7. **Dashboard**
- View your complete analysis history
- Track personal health statistics
- Access quick actions for all features
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