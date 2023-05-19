import './App.css';
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const baseURL = "http://localhost:8888/";

function App() {
    const [post, setPost] = useState(null);

    useEffect(() => {
        axios.get(baseURL).then((response) => {
            setPost(response.data);
        });
    }, []);

    if (!post) return null;

    return (
        <div>
            <p>{post["time"]}</p>
        </div>
    );
}

export default App;
