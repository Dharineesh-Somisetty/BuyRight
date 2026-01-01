import { useState } from 'react';
import UploadSection from './components/UploadSection';
import LoadingAnalysis from './components/LoadingAnalysis';
import ResultsDashboard from './components/ResultsDashboard';

import { getProductByBarcode } from './services/api';

function App() {
  const [view, setView] = useState('upload'); // 'upload' | 'loading' | 'results'
  const [analysisData, setAnalysisData] = useState(null);
  const [selectedMode, setSelectedMode] = useState('BULK');
  const [uploadedImage, setUploadedImage] = useState(null);
  const [scanText, setScanText] = useState(null);
  const [productMetadata, setProductMetadata] = useState(null);

  const handleAnalysisStart = (imageFile, mode) => {
    setUploadedImage(imageFile);
    setScanText(null);
    setProductMetadata(null); // Reset metadata for new manual upload
    setSelectedMode(mode);
    setView('loading');
  };

  const handleBarcodeSearch = async (barcode) => {
    try {
      const product = await getProductByBarcode(barcode);

      if (product && product.ingredients_text) {
        setScanText(product.ingredients_text);
        setProductMetadata({
          name: product.name,
          brand: product.brand,
          image: product.image_url
        });
        setUploadedImage(null);
        setView('loading'); // Starts analysis
      } else {
        alert('Product found but no ingredients listed.');
      }
    } catch (error) {
      if (error.response && error.response.status === 404) {
        alert('Product not found in database or OpenFoodFacts.');
      } else {
        alert(`Network Error: ${error.message}. Check backend connection.`);
      }
    }
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
    setScanText(null);
    setProductMetadata(null);
  };

  return (
    <div className="min-h-screen gradient-bg">
      {view === 'upload' && (
        <UploadSection
          onAnalysisStart={handleAnalysisStart}
          onBarcodeSearch={handleBarcodeSearch}
        />
      )}

      {view === 'loading' && (
        <LoadingAnalysis
          imageFile={uploadedImage}
          initialText={scanText}
          mode={selectedMode}
          onComplete={handleAnalysisComplete}
          onError={handleAnalysisError}
        />
      )}

      {view === 'results' && analysisData && (
        <ResultsDashboard
          data={analysisData}
          productMetadata={productMetadata}
          mode={selectedMode}
          onReset={handleReset}
        />
      )}
    </div>
  );
}

export default App;
