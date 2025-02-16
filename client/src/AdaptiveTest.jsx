import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Box, Typography, Radio, RadioGroup, FormControlLabel, Button, Paper, CircularProgress } from '@mui/material';

const API_URL = 'http://localhost:5000';

const AdaptiveTest = () => {
    const [sessionId, setSessionId] = useState(null);
    const [question, setQuestion] = useState(null);
    const [selectedAnswer, setSelectedAnswer] = useState('');
    const [feedback, setFeedback] = useState(null);
    const [questionCount, setQuestionCount] = useState(0);
    const [recommendations, setRecommendations] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        startSession();
    }, []);

    const startSession = async () => {
        try {
            setLoading(true);
            const response = await axios.post(`${API_URL}/api/session/start`, {}, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            console.log('Session response:', response.data);  // Debug log
            const sid = response.data.session_id.toString();  // Convert to string
            setSessionId(sid);
            await fetchQuestion(sid);
        } catch (error) {
            console.error('Error starting session:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchQuestion = async (sid) => {
        try {
            setLoading(true);
            console.log('Fetching question for session:', sid);  // Debug log
            const response = await axios.get(`${API_URL}/api/questions/adaptive/${sid}`, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            console.log('Question response:', response.data);  // Debug log
            setQuestion(response.data);
            setSelectedAnswer('');
            setFeedback(null);
        } catch (error) {
            console.error('Error details:', error.response || error);
            if (error.response?.status === 404) {
                // If session is invalid, start a new one
                startSession();
            }
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        console.log('Submitting answer:', selectedAnswer); // Debug log
        
        if (!selectedAnswer) {
            alert('Please select an answer');
            return;
        }

        try {
            console.log('Session ID:', sessionId);
            console.log('Question ID:', question.id);
            const response = await axios.post(
                `${API_URL}/api/questions/check/${sessionId}/${question.id}`,
                { answer: selectedAnswer },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            console.log('Submit response:', response.data); // Debug log
            setFeedback(response.data);
            setQuestionCount(prev => prev + 1);
            
            if (response.data.recommendations) {
                setRecommendations(response.data.recommendations);
            } else if (questionCount < 19) {
                setTimeout(() => fetchQuestion(sessionId), 2000);
            }
        } catch (error) {
            console.error('Error submitting answer:', error);
        }
    };

    if (loading && !question) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
                <CircularProgress />
            </Box>
        );
    }

    if (recommendations) {
        return (
            <Paper elevation={3} sx={{ maxWidth: 600, mx: 'auto', mt: 4, p: 4 }}>
                <Typography variant="h4" gutterBottom>Test Complete!</Typography>
                <Typography variant="h5" gutterBottom>Recommendations:</Typography>
                <Box component="ul" sx={{ pl: 2 }}>
                    {recommendations.map((rec, index) => (
                        <Typography component="li" key={index} sx={{ mb: 1 }}>
                            {rec}
                        </Typography>
                    ))}
                </Box>
            </Paper>
        );
    }

    return (
        <Paper elevation={3} sx={{ maxWidth: 600, mx: 'auto', mt: 4, p: 4 }}>
            <Typography variant="h4" gutterBottom>Adaptive Test</Typography>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h6">Question {questionCount + 1}/20</Typography>
                <Typography variant="subtitle1">Difficulty: {question?.difficulty}</Typography>
            </Box>
            
            {question && (
                <Box component="form" onSubmit={handleSubmit}>
                    <Typography variant="h6" gutterBottom>{question.text}</Typography>
                    <RadioGroup
                        value={selectedAnswer}
                        onChange={(e) => setSelectedAnswer(e.target.value)}
                    >
                        {question.options.map((option, index) => (
                            <FormControlLabel
                                key={index}
                                value={option}
                                control={<Radio />}
                                label={option}
                            />
                        ))}
                    </RadioGroup>
                    <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        disabled={!selectedAnswer}
                        sx={{ mt: 2 }}
                    >
                        Submit
                    </Button>
                </Box>
            )}

            {feedback && (
                <Box sx={{ mt: 2, p: 2, bgcolor: feedback.correct ? 'success.light' : 'error.light', borderRadius: 1 }}>
                    <Typography color={feedback.correct ? 'success.dark' : 'error.dark'}>
                        {feedback.correct ? 'Correct!' : `Incorrect. The correct answer was: ${feedback.correctAnswer}`}
                    </Typography>
                    <Typography sx={{ mt: 1 }}>
                        Next difficulty level: {feedback.nextDifficulty}
                    </Typography>
                </Box>
            )}
        </Paper>
    );
};

export default AdaptiveTest; 