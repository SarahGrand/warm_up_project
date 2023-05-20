import React from 'react';

export default function Header({ time }) {
    return <div style={{
        marginTop: '1vh',
        textAlign: 'center',
        fontFamily: 'Cabin'
    }}>
        <h1>Sarah's API Widgets</h1>
        <p>Time of last query: {time}</p>
    </div>
}
