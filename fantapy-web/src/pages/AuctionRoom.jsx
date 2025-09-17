import { useState, useEffect } from "react";
import axios from "axios";

export default function AuctionRoom({ auctionId, nickname, socket }) {
  const [events, setEvents] = useState([]);
  const [teams, setTeams] = useState([
    { id: 1, name: "Team 1", budget: 1000 },
    { id: 2, name: "Team 2", budget: 1000 },
    { id: 3, name: "Team 3", budget: 1000 },
  ]);
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);

  useEffect(() => {
    if (!socket) return;
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents((prev) => [...prev, data]);

      if (data.type === "participant_joined") {
        setUsers((prev) => [...prev, data.payload]);
      }
      if (data.type === "participant_left") {
        setUsers((prev) => prev.filter((u) => u.id !== data.payload.id));
      }
      if (data.type === "team_assigned") {
        setTeams((prev) =>
          prev.map((t) =>
            t.id === data.payload.team_id
              ? { ...t, assignedTo: data.payload.participant_name }
              : t
          )
        );
      }
    };
  }, [socket]);

  const assignTeam = async (teamId) => {
    if (!selectedUser) {
      alert("Seleziona prima un utente!");
      return;
    }
    await axios.post(`http://127.0.0.1:8000/auctions/${auctionId}/assign`, {
      participant_id: selectedUser.id,
      team_id: teamId,
    });
  };

  return (
    <div className="grid grid-cols-[250px_1fr_300px] h-screen">
      {/* Colonna sinistra: Teams */}
      <aside className="bg-purple-900 text-white p-4">
        <h2 className="font-bold mb-2">Teams</h2>
        <ul>
          {teams.map((t) => (
            <li key={t.id} className="border-b py-2">
              <div className="flex justify-between">
                <span>{t.name}</span>
                <span>💰 {t.budget}</span>
              </div>
              {t.assignedTo ? (
                <p className="text-sm text-green-300">Assegnato a: {t.assignedTo}</p>
              ) : (
                <button
                  onClick={() => assignTeam(t.id)}
                  className="bg-blue-600 text-white px-2 py-1 mt-1 rounded text-xs"
                >
                  Assegna utente
                </button>
              )}
            </li>
          ))}
        </ul>
      </aside>

      {/* Area centrale */}
      <main className="bg-gray-100 p-6">
        <h2 className="font-bold text-xl mb-4">Auction Control</h2>
        <div className="bg-white shadow rounded p-4">
          <select className="border p-2 rounded">
            <option>Seleziona un giocatore</option>
          </select>
          <div className="mt-4 flex gap-2">
            <button className="bg-green-600 text-white px-4 py-2 rounded">Chiama</button>
            <button className="bg-blue-600 text-white px-4 py-2 rounded">Assegna</button>
          </div>
        </div>
      </main>

      {/* Colonna destra */}
      <aside className="bg-gray-800 text-white p-4 flex flex-col gap-4">
        <div>
          <h2 className="font-bold mb-2">Connected Users</h2>
          <ul>
            {users.map((u) => (
              <li
                key={u.id}
                className={`border-b py-1 cursor-pointer ${
                  selectedUser?.id === u.id ? "bg-blue-600" : ""
                }`}
                onClick={() => setSelectedUser(u)}
              >
                {u.name}
              </li>
            ))}
          </ul>
        </div>

        <div className="flex-1 overflow-y-auto">
          <h2 className="font-bold mb-2">Event Log</h2>
          <ul className="text-sm">
            {events.map((e, i) => (
              <li key={i}>
                {e.type}: {JSON.stringify(e.payload)}
              </li>
            ))}
          </ul>
        </div>
      </aside>
    </div>
  );
}
