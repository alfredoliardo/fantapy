// src/App.jsx
import { useEffect, useState } from "react";

function App() {
  const [ws, setWs] = useState(null);
  const [events, setEvents] = useState([]);

  const connect = async () => {
    const auctionId = prompt("Auction ID?");
    const nickname = prompt("Nickname?");
    const socket = new WebSocket(`ws://localhost:8000/ws/${auctionId}/${nickname}`);

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents((prev) => [...prev, data]);
    };

    setWs(socket);
  };

  return (
    <div>
      <button onClick={connect}>Join Auction</button>
      <h3>Events</h3>
      <ul>
        {events.map((e, i) => (
          <li key={i}>{e.type} → {JSON.stringify(e.payload)}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;
