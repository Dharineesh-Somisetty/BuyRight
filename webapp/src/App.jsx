import { useState } from 'react';
import UploadSection from './components/UploadSection';
import LoadingAnalysis from './components/LoadingAnalysis';
import ResultsDashboard from './components/ResultsDashboard';

function App() {
  const [view, setView] = useState('upload'); // 'upload' | 'loading' | 'results'
  const [analysisData, setAnalysisData] = useState(null);
  const [selectedMode, setSelectedMode] = useState('BULK');
  const [uploadedImage, setUploadedImage] = useState(null);

  const handleAnalysisStart = (imageFile, mode) => {
    setUploadedImage(imageFile);
    setSelectedMode(mode);
    setView('loading');
  };

  const handleAnalysisComplete = (data) => {
    setAnalysisData(data);
    setView('results');
  };

  const handleAnalysisError = (error) => {
    console.error('Analysis error:', error);
    alert(`Analysis failed: ${error.message}`);
    setView('upload');
  };

  const handleReset = () => {
    setView('upload');
    setAnalysisData(null);
    setUploadedImage(null);
  };

  return (
    <div className="min-h-screen gradient-bg">
      {view === 'upload' && (
        <UploadSection onAnalysisStart={handleAnalysisStart} />
      )}

      {view === 'loading' && (
        <LoadingAnalysis
          imageFile={uploadedImage}
          mode={selectedMode}
          onComplete={handleAnalysisComplete}
          onError={handleAnalysisError}
        />
      )}

      {view === 'results' && analysisData && (
        <ResultsDashboard
          data={analysisData}
          mode={selectedMode}
          onReset={handleReset}
        />
      )}
    </div>
  );
}

export default App;
