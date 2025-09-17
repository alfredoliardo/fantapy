import { useState } from "react";
import axios from "axios";
import AuctionRoom from "./pages/AuctionRoom";

function App() {
  const [auctionId, setAuctionId] = useState(null);
  const [socket, setSocket] = useState(null);
  const [nickname, setNickname] = useState("");

  const createAuction = async () => {
    const name = prompt("Auction name?");
    const host = prompt("Host name?");
    const res = await axios.post("http://127.0.0.1:8000/auctions", null, {
      params: { name, host_name: host },
    });
    setAuctionId(res.data.auction_id);
    setNickname(host);
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/${res.data.auction_id}/${host}`);
    setSocket(ws);
  };

  if (auctionId && socket) {
    return <AuctionRoom auctionId={auctionId} nickname={nickname} socket={socket} />;
  }

  return (
    <div className="p-10">
      <h1 className="text-2xl font-bold mb-4">Fantapy Auction</h1>
      <button className="bg-indigo-600 text-white px-4 py-2 rounded" onClick={createAuction}>
        Create Auction
      </button>
    </div>
  );
}

export default App;
