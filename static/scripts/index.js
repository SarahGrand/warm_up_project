function App({ results }) {
    const results_json = JSON.parse(results)
    return <WeatherWidget query_time={results_json["time"]} {...results_json["tlv_weather"]} />
}

function WeatherWidget({ query_time, response_time, temp }) {
    return <div>
        <h2>Current Weather in Tel Aviv</h2>
        <p>API queried at: {query_time}</p>
        <p>{response_time}</p>
        <p>{temp}</p>
    </div>
}

function HistoryWidget({ query_time, response_time, fact, year }) {
    return <div>
        <h2>History Widget</h2>
        <p>{query_time}</p>
        <p>{response_time}</p>
        <p>{fact}</p>
        <p>{year}</p>
    </div>
}

var root = document.getElementById('root');
var results = root.getAttribute('results');
ReactDOM.render(<App results={results} />, root);