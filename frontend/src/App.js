import './App.css';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Header from './Header';
import Body from './Body';

const baseURL = "http://localhost:8888/";

function App() {
    const [post, setPost] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        // TODO make this async
        axios.get(baseURL).then((response) => {
            setPost(response.data);
        }).catch(error => {
            setError(error);
        });
    }, []);

    if (error) return `Error: ${error.message}`;
    if (!post) return "No data.";

    return (
        <div>
            <Header time={post["time"]} />
            <Body data={post} />
        </div>
    );
}

export default App;
