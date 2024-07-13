import React, { useEffect, useState } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:3001';

function App() {
  const [message, setMessage] = useState('');
  const [players, setPlayers] = useState([]);
  const [tables, setTables] = useState([]);
  const [selectedTable, setSelectedTable] = useState(null);
  const [newPlayerName, setNewPlayerName] = useState('');
  const [newPlayerBankroll, setNewPlayerBankroll] = useState(0);
  const [newTableName, setNewTableName] = useState('');
  const [maxPlayers, setMaxPlayers] = useState(9);
  const [minBuyIn, setMinBuyIn] = useState(50);
  const [maxBuyIn, setMaxBuyIn] = useState(500);
  const [smallBlind, setSmallBlind] = useState(10);
  const [bigBlind, setBigBlind] = useState(20);
  const [antee, setAntee] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMessage();
    fetchTables();
  }, []);

  const fetchMessage = async () => {
    try {
      const response = await fetch(`${API_URL}/`);
      const text = await response.text();
      setMessage(text);
    } catch (err) {
      setError('Failed to fetch message');
      console.error(err);
    }
  };

  const fetchTables = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/tables`);
      const data = await response.json();
      setTables(data);
    } catch (err) {
      setError('Failed to fetch tables');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createPlayer = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/add_player`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newPlayerName, bankroll: newPlayerBankroll }),
      });
      const data = await response.json();
      if (data.message) {
        setPlayers([...players, { name: newPlayerName, bankroll: newPlayerBankroll }]);
        setNewPlayerName('');
        setNewPlayerBankroll(0);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to create player');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const createTable = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/set_table`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newTableName, max_players: maxPlayers, min_buy_in: minBuyIn, max_buy_in: maxBuyIn, small_blind: smallBlind, big_blind: bigBlind, antee }),
      });
      const data = await response.json();
      if (data.message) {
        fetchTables();
        setNewTableName('');
        setMaxPlayers(9);
        setMinBuyIn(50);
        setMaxBuyIn(500);
        setSmallBlind(10);
        setBigBlind(20);
        setAntee(0);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to create table');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const deleteTable = async (tableName) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/delete_table`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: tableName }),
      });
      const data = await response.json();
      if (data.message) {
        fetchTables();
        setSelectedTable(null);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to delete table');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const addPlayerToTable = async (playerName) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/add_player_to_table`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_name: playerName, table_name: selectedTable.name }),
      });
      const data = await response.json();
      if (data.message) {
        fetchTables();
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to add player to table');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const removePlayerFromTable = async (playerName) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/remove_player_from_table`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_name: playerName, table_name: selectedTable.name }),
      });
      const data = await response.json();
      if (data.message) {
        fetchTables();
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to remove player from table');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const performTableAction = async (action) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/${action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ table_name: selectedTable.name }),
      });
      const data = await response.json();
      if (data.message) {
        fetchTables();
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError(`Failed to ${action.replace('_', ' ')}`);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        {loading && <p>Loading...</p>}
        {error && <p className="error">{error}</p>}
        <p>{message}</p>
        <h2>Manage Players</h2>
        <div>
          <input
            type="text"
            placeholder="Player Name"
            value={newPlayerName}
            onChange={(e) => setNewPlayerName(e.target.value)}
          />
          <input
            type="number"
            placeholder="Bankroll"
            value={newPlayerBankroll}
            onChange={(e) => setNewPlayerBankroll(parseInt(e.target.value))}
          />
          <button onClick={createPlayer}>Create Player</button>
        </div>
        <h2>Players List</h2>
        <ul>
          {players.map((player) => (
            <li key={player.name}>{player.name} - ${player.bankroll}</li>
          ))}
        </ul>
        <h2>Manage Tables</h2>
        <div>
          <input
            type="text"
            placeholder="Table Name"
            value={newTableName}
            onChange={(e) => setNewTableName(e.target.value)}
          />
          <input
            type="number"
            placeholder="Max Players"
            value={maxPlayers}
            onChange={(e) => setMaxPlayers(parseInt(e.target.value))}
          />
          <input
            type="number"
            placeholder="Min Buy-In"
            value={minBuyIn}
            onChange={(e) => setMinBuyIn(parseInt(e.target.value))}
          />
          <input
            type="number"
            placeholder="Max Buy-In"
            value={maxBuyIn}
            onChange={(e) => setMaxBuyIn(parseInt(e.target.value))}
          />
          <input
            type="number"
            placeholder="Small Blind"
            value={smallBlind}
            onChange={(e) => setSmallBlind(parseInt(e.target.value))}
          />
          <input
            type="number"
            placeholder="Big Blind"
            value={bigBlind}
            onChange={(e) => setBigBlind(parseInt(e.target.value))}
          />
          <input
            type="number"
            placeholder="Antee"
            value={antee}
            onChange={(e) => setAntee(parseInt(e.target.value))}
          />
          <button onClick={createTable}>Create Table</button>
        </div>
        <h2>Tables List</h2>
        <ul>
          {tables.map((table) => (
            <li key={table.name}>
              {table.name} - {table.players.length} players
              <button onClick={() => setSelectedTable(table)}>Select</button>
              <button onClick={() => deleteTable(table.name)}>Delete</button>
            </li>
          ))}
        </ul>
        {selectedTable && (
          <div>
            <h2>Manage {selectedTable.name}</h2>
            <h3>Players at Table</h3>
            <ul>
              {selectedTable.players.map((player) => (
                <li key={player.name}>
                  {player.name} - ${player.bankroll} - {player.status}
                  <button onClick={() => removePlayerFromTable(player.name)}>Remove</button>
                </li>
              ))}
            </ul>
            <h3>Add Player to Table</h3>
            <ul>
              {players.filter(p => !selectedTable.players.some(sp => sp.name === p.name)).map((player) => (
                <li key={player.name}>
                  {player.name} - ${player.bankroll}
                  <button onClick={() => addPlayerToTable(player.name)}>Add</button>
                </li>
              ))}
            </ul>
            <div className="button-container">
              <button onClick={() => performTableAction('reshuffle')}>Re-shuffle Deck</button>
              <button onClick={() => performTableAction('deal_cards')}>Deal Cards</button>
              <button onClick={() => performTableAction('deal_flop')}>Deal Flop</button>
              <button onClick={() => performTableAction('deal_turn')}>Deal Turn</button>
              <button onClick={() => performTableAction('deal_river')}>Deal River</button>
              <button onClick={() => performTableAction('determine_winner')}>Determine Winner</button>
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
