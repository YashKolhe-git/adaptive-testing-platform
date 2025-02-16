import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { theme } from './theme';
import Layout from './components/Layout';
import Home from './components/Home';
import About from './components/About';
import Contact from './components/Contact';
import { AuthProvider } from './contexts/AuthContext';
import AdminLogin from './components/Auth/AdminLogin';
import Signup from './components/Auth/Signup';
import AdaptiveTest from './AdaptiveTest';

function App() {
  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/about" element={<About />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/admin-login" element={<AdminLogin />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/adaptive-test" element={<AdaptiveTest />} />
            </Routes>
          </Layout>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App; 