import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [audioFile, setAudioFile] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [summary, setSummary] = useState('');
  const [email, setEmail] = useState('');

  const handleFileChange = (e) => {
    setAudioFile(e.target.files[0]);
  };

  const handleTranscribe = async () => {
    const formData = new FormData();
    formData.append('audio', audioFile);
    const response = await axios.post('/transcribe', formData);
    setTranscription(response.data.transcription);
  };

  const handleSummarize = async () => {
    const response = await axios.post('/summarize', { text: transcription });
    setSummary(response.data.summary);
  };

  const handleDraftEmail = async () => {
    const response = await axios.post('/draft-email', { summary });
    setEmail(response.data.email);
  };

  return (
    <div>
      <h1>Neural Value Authority (NVA)</h1>
      <div>
        <h2>Upload Audio File</h2>
        <input type="file" accept="audio/*" onChange={handleFileChange} />
        <button onClick={handleTranscribe}>Transcribe</button>
      </div>
      <div>
        <h2>Transcription</h2>
        <p>{transcription}</p>
      </div>
      <div>
        <h2>Summary</h2>
        <p>{summary}</p>
        <button onClick={handleSummarize}>Summarize</button>
      </div>
      <div>
        <h2>Draft Email</h2>
        <p>{email}</p>
        <button onClick={handleDraftEmail}>Draft Email</button>
      </div>
    </div>
  );
}

export default App;