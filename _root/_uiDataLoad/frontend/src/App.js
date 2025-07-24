import React, { useState } from 'react';
import {
  Container, Box, Typography, Card, CardContent, Button, TextField, Snackbar, Alert, CircularProgress, LinearProgress, ThemeProvider, createTheme, CssBaseline, MenuItem, Select, FormControl, InputLabel, Link
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import axios from 'axios';

//const API_BASE = 'http://localhost:8000/api'; // Changed for deployment
const API_BASE = '/api'; // Changed for deployment
const WORKFLOW_NAME = 'dsilaslogicapp';
const FILE_SOURCE_OPTIONS = [
  { label: 'Founder Hub', value: 'founderhub' },
  { label: 'Crunch Base', value: 'crunchbase' },
  { label: 'Others', value: 'others' },
];
const SHAREPOINT_LINK = 'https://microsoftapc-my.sharepoint.com/personal/ramganeshvj_microsoft_com/Lists/DSILead%20Allocation%20System/AllItems.aspx';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00bcd4',
      contrastText: '#fff',
    },
    secondary: {
      main: '#ff4081',
      contrastText: '#fff',
    },
    background: {
      default: '#181a20',
      paper: '#23272f',
    },
    success: {
      main: '#00e676',
    },
    error: {
      main: '#ff1744',
    },
    info: {
      main: '#2979ff',
    },
    warning: {
      main: '#ffc400',
    },
    text: {
      primary: '#e3e3e3',
      secondary: '#b0b0b0',
    },
  },
  typography: {
    fontFamily: 'Montserrat, Roboto, Arial',
    h3: {
      fontWeight: 800,
      letterSpacing: 1.5,
    },
    h5: {
      fontWeight: 700,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
      letterSpacing: 1,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #23272f 60%, #181a20 100%)',
          boxShadow: '0 4px 32px 0 rgba(0, 188, 212, 0.10)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          fontSize: '1.1em',
          padding: '0.6em 2.2em',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          background: '#23272f',
          borderRadius: 8,
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(90deg, #23272f 0%, #00bcd4 100%)',
          borderRadius: 5,
        },
        bar: {
          background: 'linear-gradient(90deg, #ff4081 0%, #00e676 100%)',
        },
      },
    },
  },
});

function App() {
  // File source state
  const [fileSource, setFileSource] = useState('founderhub');
  // File upload state
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState('');

  // Logic App status state
  const [checking, setChecking] = useState(false);
  const [statusResult, setStatusResult] = useState(null);
  const [statusError, setStatusError] = useState('');

  // Snackbar
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'text/csv' && !selectedFile.name.toLowerCase().endsWith('.csv')) {
        setSnackbar({ open: true, message: 'Invalid file type. Please upload a CSV file.', severity: 'error' });
        setFile(null);
        e.target.value = null; // Reset file input for re-selection
        return;
      }
      setFile(selectedFile);
      setUploadSuccess(false); // Hide status on new file selection
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setUploadError('');
    setStatusResult(null);
    setStatusError('');
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('source', fileSource);
      const res = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setUploadSuccess(true);
      setSnackbar({ open: true, message: `File '${res.data.filename}' uploaded successfully!`, severity: 'success' });
      // Automatically start Logic App status check after upload
      handleStatusCheck();
    } catch (err) {
      setUploadError(err.response?.data?.detail || 'Upload failed');
      setSnackbar({ open: true, message: err.response?.data?.detail || 'Upload failed', severity: 'error' });
    } finally {
      setUploading(false);
    }
  };

  const handleStatusCheck = async () => {
    setChecking(true);
    setStatusError('');
    setStatusResult(null);
    try {
      const res = await axios.get(`${API_BASE}/logicapp-status/${WORKFLOW_NAME}`);
      setStatusResult(res.data);
      setSnackbar({ open: true, message: `Status: ${res.data.status}`, severity: 'info' });
    } catch (err) {
      setStatusError(err.response?.data?.detail || 'Status check failed');
      setSnackbar({ open: true, message: err.response?.data?.detail || 'Status check failed', severity: 'error' });
    } finally {
      setChecking(false);
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', width: '100vw', bgcolor: 'background.default', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Container maxWidth="sm" sx={{ py: 6 }}>
          <Typography variant="h3" align="center" gutterBottom sx={{ color: 'primary.main', letterSpacing: 2 }}>
            Lead Distribution Loader
          </Typography>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {/* File Source Selection */}
            <Card elevation={8} sx={{ borderRadius: 4 }}>
              <CardContent>
                <FormControl fullWidth variant="outlined">
                  <InputLabel id="file-source-label" sx={{ color: 'primary.main' }}>Select File Source</InputLabel>
                  <Select
                    labelId="file-source-label"
                    id="file-source"
                    value={fileSource}
                    label="Select File Source"
                    onChange={e => {
                      setFileSource(e.target.value);
                      setUploadSuccess(false); // Hide status on source change
                    }}
                    sx={{ color: 'primary.main', background: '#23272f', borderRadius: 2 }}
                  >
                    {FILE_SOURCE_OPTIONS.map(opt => (
                      <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
            {/* File Upload Card */}
            <Card elevation={8} sx={{ borderRadius: 4 }}>
              <CardContent>
                <Typography variant="h5" gutterBottom sx={{ color: 'secondary.main' }}>
                  <CloudUploadIcon sx={{ verticalAlign: 'middle', color: 'primary.main', mr: 1 }} /> Upload File
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Button variant="contained" component="label" color="primary" startIcon={<CloudUploadIcon />}>
                    Choose File
                    <input type="file" hidden onChange={handleFileChange} accept=".csv" />
                  </Button>
                  <Typography variant="body1" sx={{ color: 'text.secondary' }}>{file ? file.name : 'No file selected'}</Typography>
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Button
                    variant="contained"
                    color="success"
                    onClick={handleUpload}
                    disabled={!file || uploading}
                    startIcon={uploading ? <CircularProgress size={20} color="inherit" /> : <CheckCircleIcon />}
                  >
                    {uploading ? 'Uploading...' : 'Upload'}
                  </Button>
                </Box>
                {uploadError && <Alert severity="error" sx={{ mt: 2 }}>{uploadError}</Alert>}
              </CardContent>
            </Card>
            {/* File Processing Status Card */}
            {uploadSuccess && (
              <Card elevation={8} sx={{ borderRadius: 4 }}>
                <CardContent>
                  <Typography variant="h5" gutterBottom sx={{ color: 'secondary.main' }}>
                    File Processing Status
                  </Typography>
                  {checking && (
                    <Box sx={{ width: '100%', mt: 2 }}>
                      <LinearProgress color="info" sx={{ height: 12, borderRadius: 6, background: 'linear-gradient(90deg, #23272f 0%, #00bcd4 100%)' }} />
                      <Typography variant="body2" align="center" sx={{ mt: 1, color: 'info.main', fontWeight: 600, letterSpacing: 1 }}>
                        Checking file processing status...
                      </Typography>
                    </Box>
                  )}
                  {statusResult && (
                    <Alert severity={statusResult.status === 'Succeeded' ? 'success' : statusResult.status === 'Failed' ? 'error' : 'info'} sx={{ mt: 2 }}>
                      <strong>Status:</strong> {statusResult.status}<br />
                      {statusResult.status === 'Succeeded' && (
                        <span>
                          File processed successfully. Please check the records at{' '}
                          <Link href={SHAREPOINT_LINK} target="_blank" rel="noopener" underline="always" color="info.main">
                            this link
                          </Link>.
                        </span>
                      )}
                      {statusResult.status === 'Failed' && statusResult.error && (
                        <span><strong>Error:</strong> {statusResult.error}</span>
                      )}
                    </Alert>
                  )}
                  {statusError && <Alert severity="error" sx={{ mt: 2 }}>{statusError}</Alert>}
                </CardContent>
              </Card>
            )}
          </Box>
          <Snackbar
            open={snackbar.open}
            autoHideDuration={4000}
            onClose={() => setSnackbar({ ...snackbar, open: false })}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
          >
            <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
              {snackbar.message}
            </Alert>
          </Snackbar>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App; 