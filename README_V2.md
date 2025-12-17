# 🎉 Bolão Copa 2026 - Modern Redesign

A completely fresh, modern Flask application for World Cup 2026 betting pool.

## ✨ Features

### 🎨 **Modern Design**
- **Tailwind CSS** - Utility-first CSS framework
- **Inter Font** - Clean, professional typography
- **Gradient Backgrounds** - Beautiful color transitions
- **Card-based UI** - Modern, clean components
- **Responsive Design** - Mobile-first approach

### 🏗️ **Clean Architecture**
- Simple, readable Flask code
- Embedded templates (easy to deploy)
- SQLite database
- Session-based authentication
- No complex dependencies

### 📱 **Pages**

1. **Login Page**
   - Clean card design
   - Simple username/password auth
   - Flash messages for feedback

2. **Dashboard**
   - Beautiful stats cards:
     - Total Points (blue gradient)
     - Exact Matches (green gradient)
     - Total Bets (purple gradient)
     - Matches Finished (orange gradient)
   - Quick action cards
   - Personalized welcome message

3. **Ranking**
   - Full leaderboard table
   - Medal icons (🥇🥈🥉) for top 3
   - Highlight current user
   - Circular badges for stats
   - Clean, readable design

4. **Matches/Betting**
   - Phase filter dropdown
   - Large, easy-to-use score inputs
   - Real-time result display
   - Sticky save button
   - Card-based match display

## 🚀 Running the App

```bash
# Start the application
python3 app_v2.py

# Access in browser
http://localhost:5001
```

## 👥 Test Accounts

All users have password: `senha123`

- bernardo
- João Silva
- Maria Santos
- Pedro Oliveira
- Ana Costa
- Carlos Souza
- Juliana Lima
- Ricardo Alves
- Fernanda Rocha
- Lucas Martins
- Beatriz Pereira

## 📊 Database Structure

The app uses the existing `bolao_2026_dev.db` with:
- `users` - User accounts
- `fixtures` - All matches
- `bet` - User predictions
- `palpites_gerais` - General predictions

## 🎯 Design Philosophy

### **Simplicity First**
- No custom CSS files
- No complex build process
- Single file deployment
- Inline styles when needed

### **Modern UX**
- Clear visual hierarchy
- Generous spacing
- Bold typography
- Obvious interactive elements
- Instant feedback

### **Performance**
- Minimal dependencies
- Efficient SQL queries
- Small page sizes
- Fast load times

## 📱 Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

All components adapt fluidly across screen sizes.

## 🎨 Color Scheme

- **Primary Blue**: `#2563eb` - Main actions, branding
- **Green**: `#10b981` - Success, exact matches
- **Purple**: `#8b5cf6` - Secondary stats
- **Orange**: `#f97316` - Highlights, warnings
- **Slate**: `#475569` - Text, neutrals

## 🔧 Tech Stack

- **Flask** - Web framework
- **Tailwind CSS** - Styling (CDN)
- **SQLite** - Database
- **Jinja2** - Templates
- **Python 3** - Backend

## 📝 Code Quality

- Clean, readable code
- Consistent naming
- Helpful comments
- Logical structure
- Easy to maintain

---

**Built with ❤️ for Copa do Mundo 2026**
