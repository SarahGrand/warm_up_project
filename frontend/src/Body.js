import React from 'react';
import Grid from '@mui/material/Grid';
import CloudIcon from '@mui/icons-material/Cloud';
import PublicIcon from '@mui/icons-material/Public';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';

export default function Body({ data }) {
    return <div style={{
        color: 'black',
        margin: '5vw'
    }}>
        <Grid container spacing={12} justifyContent="space-around">
            <WeatherWidget {...data["tlv_weather"]} />
            <HistoryWidget {...data["history_facts"]} />
            <SpaceWidget {...data["space_imgs"]} />
        </Grid>
    </div>
}

function Widget(props) {
    return <Grid item xs={12} sm={4}>
        <div style={{
            backgroundColor: '#edf9fa',
            borderRadius: '15px',
            boxShadow: '4px 4px 5px 1px #d5e7e8',
            width: '25vw',
            height: '25vw',
            border: '2px solid #8ea2a3',
            textAlign: 'center',
            fontFamily: 'Cabin',
        }}>
            {props.children}
        </div>
    </Grid>
}

function WeatherWidget({ response_time, temp, humidity, windspeed, visibility }) {
    return <Widget>
        <h3>Current Weather in Tel Aviv, Israel</h3>
        <p>Reponse time: {response_time} ms</p>
        <CloudIcon fontSize='large' />
        <p>Temperature: {temp}°F</p>
        <p>Humidity: {humidity}%</p>
        <p>Wind speed: {windspeed} mph</p>
        <p>Visibility: {visibility} miles</p>
    </Widget>
}

function HistoryWidget({ response_time, fact, year }) {
    return <Widget>
        <h3>On this day in history...</h3>
        <p>Reponse time: {response_time} ms</p>
        <PublicIcon fontSize='large' />
        <p style={{ textAlign: 'center' }}>
            In the year {year},<br />
            {fact}
        </p>
    </Widget>
}

function SpaceWidget({ response_time, img_title, img_url }) {
    return <Widget>
        <h3>Astronomy image of the day from NASA</h3>
        <p>Reponse time: {response_time} ms</p>
        <RocketLaunchIcon fontSize='large' />
        <p>{img_title}</p>
        <img src={img_url} width="50%" />
    </Widget>
}
