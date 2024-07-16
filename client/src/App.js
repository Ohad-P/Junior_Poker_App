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
      console.error('Fetch message error:', err);
    }
  };

  const fetchTables = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/tables`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTables(data);
      console.log('Fetched tables:', data);
    } catch (err) {
      setError('Failed to fetch tables');
      console.error('Fetch tables error:', err);
    } finally {
      setLoading(false);
    }
  };

  const createPlayer = async () => {
    console.log('Creating player with name:', newPlayerName, 'and bankroll:', newPlayerBankroll);
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
      console.log('Create player response:', data);
      if (data.message) {
        setPlayers([...players, { name: newPlayerName, bankroll: newPlayerBankroll }]);
        setNewPlayerName('');
        setNewPlayerBankroll(0);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to create player');
      console.error('Create player error:', err);
    } finally {
      setLoading(false);
    }
  };

  const createTable = async () => {
    console.log('Creating table with name:', newTableName, 'max players:', maxPlayers, 'min buy-in:', minBuyIn, 'max buy-in:', maxBuyIn, 'small blind:', smallBlind, 'big blind:', bigBlind, 'antee:', antee);
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
      console.log('Create table response:', data);
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
      console.error('Create table error:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteTable = async (tableName) => {
    console.log('Deleting table with name:', tableName);
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
      console.log('Delete table response:', data);
      if (data.message) {
        fetchTables();
        setSelectedTable(null);
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to delete table');
      console.error('Delete table error:', err);
    } finally {
      setLoading(false);
    }
  };

  const addPlayerToTable = async (playerName) => {
    console.log('Adding player to table:', playerName);
    try {
      setLoading(true);
      console.log(`POST request to ${API_URL}/add_player_to_table with player_name: ${playerName} and table_name: ${selectedTable.name}`);
      const response = await fetch(`${API_URL}/add_player_to_table`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ player_name: playerName, table_name: selectedTable.name }),
      });
      const data = await response.json();
      console.log('Add player to table response:', data);
      if (data.message) {
        // Refetch the tables to update the UI
        fetchTables();
        // Update the selectedTable state to include the new player
        setSelectedTable(prev => ({
          ...prev,
          players: [...prev.players, { name: playerName, bankroll: 0, status: "sitting" }]
        }));
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to add player to table');
      console.error('Add player to table error:', err);
    } finally {
      setLoading(false);
    }
  };

  const removePlayerFromTable = async (playerName) => {
    console.log('Removing player from table:', playerName);
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
      console.log('Remove player from table response:', data);
      if (data.message) {
        fetchTables();
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError('Failed to remove player from table');
      console.error('Remove player from table error:', err);
    } finally {
      setLoading(false);
    }
  };

  const performTableAction = async (action) => {
    console.log('Performing table action:', action);
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
      console.log(`Table action ${action} response:`, data);
      if (data.message) {
        fetchTables();
      } else {
        setError(data.message);
      }
    } catch (err) {
      setError(`Failed to ${action.replace('_', ' ')}`);
      console.error(`Table action ${action} error:`, err);
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
        <div className="form-group">
          <label>
            Player Name:
            <input
              type="text"
              placeholder="Player Name"
              value={newPlayerName}
              onChange={(e) => setNewPlayerName(e.target.value)}
            />
          </label>
          <label>
            Bankroll:
            <input
              type="number"
              placeholder="Bankroll"
              value={newPlayerBankroll}
              onChange={(e) => setNewPlayerBankroll(parseInt(e.target.value))}
            />
          </label>
          <button onClick={createPlayer}>Create Player</button>
        </div>

        <h2>Players List</h2>
        <ul>
          {players.map((player) => (
            <li key={player.name}>{player.name} - ${player.bankroll}</li>
          ))}
        </ul>
        <h2>Manage Tables</h2>
        <div className="form-group">
          <label>
            Table Name:
            <input
              type="text"
              placeholder="Table Name"
              value={newTableName}
              onChange={(e) => setNewTableName(e.target.value)}
            />
          </label>
          <label>
            Max Players:
            <input
              type="number"
              placeholder="Max Players"
              value={maxPlayers}
              onChange={(e) => setMaxPlayers(parseInt(e.target.value))}
            />
          </label>
          <label>
            Min Buy-In:
            <input
              type="number"
              placeholder="Min Buy-In"
              value={minBuyIn}
              onChange={(e) => setMinBuyIn(parseInt(e.target.value))}
            />
          </label>
          <label>
            Max Buy-In:
            <input
              type="number"
              placeholder="Max Buy-In"
              value={maxBuyIn}
              onChange={(e) => setMaxBuyIn(parseInt(e.target.value))}
            />
          </label>
          <label>
            Small Blind:
            <input
              type="number"
              placeholder="Small Blind"
              value={smallBlind}
              onChange={(e) => setSmallBlind(parseInt(e.target.value))}
            />
          </label>
          <label>
            Big Blind:
            <input
              type="number"
              placeholder="Big Blind"
              value={bigBlind}
              onChange={(e) => setBigBlind(parseInt(e.target.value))}
            />
          </label>
          <label>
            Antee:
            <input
              type="number"
              placeholder="Antee"
              value={antee}
              onChange={(e) => setAntee(parseInt(e.target.value))}
            />
          </label>
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
