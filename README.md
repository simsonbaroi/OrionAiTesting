# PyLearnAI - Self-Learning Python Expert AI

A self-improving Python programming assistant that continuously learns from web sources and user interactions. This GitHub Pages version provides a web-based interface for the PyLearnAI system with Firebase backend integration.

## 🌟 Features

- **Interactive Chat Interface**: Ask Python programming questions and get AI-powered responses
- **Database Browser**: View and explore all database tables through a web interface
- **Admin Dashboard**: Monitor system status and trigger data collection/training
- **Real-time Statistics**: Track knowledge base items, user queries, and system performance
- **Firebase Integration**: Cloud-based data storage and synchronization

## 🚀 Live Demo

Visit the live application: **[Your GitHub Username].github.io/[Repository Name]**

## 🛠️ Setup Instructions

### 1. Deploy to GitHub Pages

1. **Fork or clone this repository**
2. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: main/master
   - Folder: /docs
3. **The site will be available at**: `https://[username].github.io/[repository-name]`

### 2. Firebase Configuration (Optional)

To enable cloud data storage and persistence:

1. **Create a Firebase project** at [console.firebase.google.com](https://console.firebase.google.com)
2. **Enable Realtime Database** in your Firebase project
3. **Update Firebase config** in `docs/app.js`:
   ```javascript
   const firebaseConfig = {
       apiKey: "your-api-key",
       authDomain: "your-project.firebaseapp.com",
       databaseURL: "https://your-project-default-rtdb.firebaseio.com/",
       projectId: "your-project-id",
       // ... other config
   };
   ```
4. **Set database rules** (for development):
   ```json
   {
     "rules": {
       ".read": true,
       ".write": true
     }
   }
   ```

## 📱 Usage

### Chat Interface
- Click "Start Chatting" to interact with the AI
- Ask any Python programming questions
- Get instant responses with code examples

### Database Browser
- Click "View Database" to explore data tables
- Browse Knowledge Base, Training Data, User Queries, and Model Metrics
- Use tabs to switch between different data types

### Admin Dashboard
- Monitor system status and performance
- Trigger data collection and model training
- View system health metrics

## 🏗️ Architecture

### Frontend (GitHub Pages)
- **HTML5** with Bootstrap 5 for responsive design
- **Vanilla JavaScript** for interactivity
- **Firebase SDK** for real-time database integration
- **Feather Icons** for consistent iconography

### Backend (Firebase)
- **Realtime Database** for data storage
- **Cloud Functions** (optional) for advanced processing
- **Authentication** (can be added for user management)

### Data Structure
```
firebase-database/
├── stats/
│   ├── knowledgeBase: number
│   ├── userQueries: number
│   └── trainingData: number
├── queries/
│   └── [query-id]/
│       ├── question: string
│       ├── answer: string
│       ├── timestamp: number
│       └── responseTime: number
├── knowledgeBase/
│   └── [item-id]/
│       ├── title: string
│       ├── sourceType: string
│       ├── qualityScore: number
│       └── createdAt: string
└── admin/
    ├── lastDataCollection: object
    └── lastTraining: object
```

## 🔧 Customization

### Styling
- Modify CSS in `docs/index.html` `<style>` section
- Bootstrap classes can be customized
- Add custom themes or color schemes

### AI Responses
- Update `generateAIResponse()` function in `docs/app.js`
- Add more sophisticated pattern matching
- Integrate with external AI APIs (OpenAI, etc.)

### Database Schema
- Modify Firebase data structure as needed
- Update display functions for new data fields
- Add new tables or collections

## 📊 Monitoring

The system tracks:
- **User Queries**: Questions asked and response times
- **Knowledge Base**: Scraped content and quality scores
- **Training Data**: Q&A pairs for model improvement
- **Model Metrics**: Performance and accuracy statistics

## 🚀 Advanced Features

### Add External AI API
```javascript
async function callExternalAI(question) {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer YOUR_API_KEY',
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            model: 'gpt-3.5-turbo',
            messages: [{ role: 'user', content: question }],
        }),
    });
    return await response.json();
}
```

### Add User Authentication
```javascript
// Add to Firebase config
import { getAuth, signInWithPopup, GoogleAuthProvider } from 'firebase/auth';

const auth = getAuth();
const provider = new GoogleAuthProvider();

function signIn() {
    signInWithPopup(auth, provider);
}
```

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Support

If you encounter any issues:
1. Check the browser console for errors
2. Verify Firebase configuration
3. Ensure GitHub Pages is properly configured
4. Open an issue in this repository

## 🎯 Roadmap

- [ ] Enhanced AI model integration
- [ ] User authentication and profiles
- [ ] Advanced data visualization
- [ ] Mobile app version
- [ ] API rate limiting and optimization
- [ ] Offline functionality with service workers

---

**PyLearnAI** - Continuously learning to help you code better! 🐍✨