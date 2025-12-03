import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './CivicResourceAgent.css';

interface Message {
  role: 'user' | 'agent';
  content: string;
  timestamp: string;
}

interface Resource {
  name: string;
  category: string;
  description: string;
  contact?: string;
  url?: string;
  eligibility?: string;
  next_step?: string;
  location?: string;
  hours?: string;
}

interface CivicResponse {
  success: boolean;
  response: string;
  resources: Resource[];
  conversation_stage: string;
  needs_category: string;
  location: string;
  urgency_level: string;
  response_time_ms?: number;
  execution_time_ms?: number;
  step_timings?: {[key: string]: number};
  timestamp: string;
  session_id: string;
  error?: string;
}

function getCurrentTime() {
  return new Date().toLocaleTimeString('en-US', { hour12: false });
}

function linkifyText(text: string) {
  // More comprehensive regex to capture full URLs with paths
  const urlRegex = /(https?:\/\/[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+)/g;
  
  return text.split(urlRegex).map((part, index) => {
    if (urlRegex.test(part)) {
      // Ensure URL has protocol
      const href = part.startsWith('http') ? part : `https://${part}`;
      return (
        <a 
          key={index} 
          href={href} 
          target="_blank" 
          rel="noopener noreferrer"
          style={{ 
            color: 'var(--accent-blue)', 
            textDecoration: 'underline',
            wordBreak: 'break-all'
          }}
        >
          {part}
        </a>
      );
    }
    return part;
  });
}

// Also linkify agent responses 
function linkifyMarkdown(text: string) {
  // Convert URLs to markdown links for ReactMarkdown, and clean up markdown formatting
  const urlRegex = /(https?:\/\/[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+)/g;
  
  // First handle cases like "**Website: https://example.com**" 
  let processedText = text.replace(/\*\*([^*]*)(https?:\/\/[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+)([^*]*)\*\*/g, 
    (match, before, url, after) => {
      const href = url.startsWith('http') ? url : `https://${url}`;
      return `**${before}[${url}](${href})${after}**`;
    });
  
  // Then handle standalone URLs
  processedText = processedText.replace(urlRegex, (url) => {
    // Skip if already processed as part of markdown link
    if (processedText.includes(`[${url}](`) || processedText.includes(`](${url})`)) {
      return url;
    }
    const href = url.startsWith('http') ? url : `https://${url}`;
    return `[${url}](${href})`;
  });
  
  return processedText;
}

const CivicResourceAgent: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'agent',
      content: 'Welcome to Civic Resource Agent! I help find local resources in Peoria. Ask me about housing, food, transportation, healthcare, employment, or other civic services.',
      timestamp: getCurrentTime()
    }
  ]);
  
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSessionId] = useState<string>(() => {
    // Generate session ID
    return `civic_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  });
  // Accumulated resources found by the agent (starts empty)
  const [accumulatedResources, setAccumulatedResources] = useState<Resource[]>([]);
  const [resourcesUpdated, setResourcesUpdated] = useState(false);
  const [showConfig, setShowConfig] = useState(false);
  const [showPerformance, setShowPerformance] = useState(false);
  const [performanceData, setPerformanceData] = useState<{execution_time_ms?: number, step_timings?: {[key: string]: number}} | null>(null);
  const [apiKeys, setApiKeys] = useState<{anthropic: string, serper: string}>({
    anthropic: localStorage.getItem('anthropic_key') || '',
    serper: localStorage.getItem('serper_key') || ''
  });
  
  // Streaming state
  const [streamingMode, setStreamingMode] = useState(true); // Enable streaming by default
  const [streamingEvents, setStreamingEvents] = useState<string[]>([]);
  const [showStreamingPanel, setShowStreamingPanel] = useState(false);
  const [thinkingLogCollapsed, setThinkingLogCollapsed] = useState(false);
  const [allStreamingEvents, setAllStreamingEvents] = useState<{timestamp: string, events: string[]}[]>([]);
  const [thinkingPanelExpanded, setThinkingPanelExpanded] = useState(false);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check if we can connect to backend
  const [backendConnected, setBackendConnected] = useState(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    // Check backend connection on mount
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      const response = await fetch('http://localhost:8001/health');
      setBackendConnected(response.ok);
    } catch (error) {
      console.log('Backend not available on localhost:8001, trying proxy...');
      try {
        const response = await fetch('/api/health');
        setBackendConnected(response.ok);
      } catch (proxyError) {
        setBackendConnected(false);
      }
    }
  };

  const testApiKey = async () => {
    if (!apiKeys.anthropic.trim()) {
      alert('Please enter an Anthropic API key first!');
      return;
    }
    
    try {
      const response = await fetch('/api/test-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ anthropic_key: apiKeys.anthropic })
      });
      
      const result = await response.json();
      if (result.valid) {
        alert('✅ API key is valid!');
      } else {
        alert(`❌ API key failed: ${result.error}`);
      }
    } catch (error) {
      alert(`❌ Error testing API key: ${error}`);
    }
  };

  const saveApiKeys = () => {
    if (!apiKeys.anthropic.trim()) {
      alert('Anthropic API key is required!');
      return;
    }
    localStorage.setItem('anthropic_key', apiKeys.anthropic);
    localStorage.setItem('serper_key', apiKeys.serper);
    setShowConfig(false);
    alert('✅ API keys saved!');
  };

  const sendMessageStreaming = async () => {
    if (!input.trim() || isLoading) return;
    
    // Debug: Log API keys (first few chars only for security)
    console.log('Anthropic key:', apiKeys.anthropic ? apiKeys.anthropic.substring(0, 10) + '...' : 'NOT SET');
    console.log('Serper key:', apiKeys.serper ? apiKeys.serper.substring(0, 10) + '...' : 'NOT SET');
    
    if (!apiKeys.anthropic) {
      setShowConfig(true);
      return;
    }

    const userMessage = input.trim();
    const timestamp = getCurrentTime();
    setInput('');
    setIsLoading(true);
    setStreamingEvents([]); // Clear previous events
    setShowStreamingPanel(true);

    // Add user message
    const newUserMessage: Message = {
      role: 'user',
      content: userMessage,
      timestamp: timestamp
    };

    setMessages(prev => [...prev, newUserMessage]);

    try {
      // Try streaming endpoint
      const response = await fetch('http://localhost:8001/api/query/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          session_id: currentSessionId,
          api_keys: {
            anthropic: apiKeys.anthropic,
            serper: apiKeys.serper || undefined
          }
        })
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let finalData: CivicResponse | null = null;

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const eventData = JSON.parse(line.slice(6));
              
              if (eventData.type === 'progress') {
                setStreamingEvents(prev => [...prev, eventData.message]);
              } else if (eventData.type === 'complete') {
                finalData = eventData.data;
              } else if (eventData.type === 'error') {
                throw new Error(eventData.message);
              }
            } catch (parseError) {
              console.warn('Failed to parse streaming event:', parseError);
            }
          }
        }
      }

      // Handle final result
      if (finalData) {
        const agentMessage: Message = {
          role: 'agent',
          content: finalData.response,
          timestamp: getCurrentTime()
        };

        setMessages(prev => [...prev, agentMessage]);
        
        // Add new resources
        if (finalData.resources && finalData.resources.length > 0) {
          const existingNames = accumulatedResources.map(r => r.name.toLowerCase());
          const newResources = finalData.resources.filter(r => 
            !existingNames.includes(r.name.toLowerCase())
          );
          
          if (newResources.length > 0) {
            setAccumulatedResources(prev => [...prev, ...newResources]);
            setResourcesUpdated(true);
          }
        }
        
        // Store performance data
        setPerformanceData({
          execution_time_ms: finalData.execution_time_ms,
          step_timings: finalData.step_timings
        });
      }

    } catch (error) {
      console.error('Streaming error:', error);
      
      const errorMessage: Message = {
        role: 'agent',
        content: "I'm having trouble processing your request. Please check that your API keys are correct and the backend is running.",
        timestamp: getCurrentTime()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      
      // Save the completed thinking process to permanent log
      if (streamingEvents.length > 0) {
        setAllStreamingEvents(prev => [...prev, {
          timestamp: getCurrentTime(),
          events: [...streamingEvents]
        }]);
      }
      
      // Keep current events visible and panel open
      setShowStreamingPanel(true);
    }
  };

  const sendMessage = async () => {
    if (streamingMode) {
      return sendMessageStreaming();
    }
    
    // Legacy non-streaming implementation
    if (!input.trim() || isLoading) return;
    
    if (!apiKeys.anthropic) {
      setShowConfig(true);
      return;
    }

    if (!backendConnected) {
      const errorMessage: Message = {
        role: 'agent',
        content: "Backend is not connected. Please make sure the backend server is running on port 8001.",
        timestamp: getCurrentTime()
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    const userMessage = input.trim();
    const timestamp = getCurrentTime();
    setInput('');
    setIsLoading(true);

    // Add user message
    const newUserMessage: Message = {
      role: 'user',
      content: userMessage,
      timestamp: timestamp
    };

    setMessages(prev => [...prev, newUserMessage]);

    try {
      // Standard API call
      let response;
      try {
        response = await fetch('http://localhost:8001/api/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: userMessage,
            session_id: currentSessionId,
            api_keys: {
              anthropic: apiKeys.anthropic,
              serper: apiKeys.serper || undefined
            }
          })
        });
      } catch (directError) {
        // Fallback to proxy
        response = await fetch('/api/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: userMessage,
            session_id: currentSessionId,
            api_keys: {
              anthropic: apiKeys.anthropic,
              serper: apiKeys.serper || undefined
            }
          })
        });
      }

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data: CivicResponse = await response.json();

      // Add agent response
      const agentMessage: Message = {
        role: 'agent',
        content: data.response,
        timestamp: getCurrentTime()
      };

      setMessages(prev => [...prev, agentMessage]);
      
      // Add new resources to accumulated resources (avoiding duplicates)
      if (data.resources && data.resources.length > 0) {
        const existingNames = accumulatedResources.map(r => r.name.toLowerCase());
        const newResources = data.resources.filter(r => 
          !existingNames.includes(r.name.toLowerCase())
        );
        
        if (newResources.length > 0) {
          setAccumulatedResources(prev => [...prev, ...newResources]);
          setResourcesUpdated(true);
        }
      }
      
      // Store performance data
      setPerformanceData({
        execution_time_ms: data.execution_time_ms,
        step_timings: data.step_timings
      });

    } catch (error) {
      console.error('Error:', error);
      
      const errorMessage: Message = {
        role: 'agent',
        content: "I'm having trouble processing your request. Please check that your API keys are correct and the backend is running.",
        timestamp: getCurrentTime()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderConfigModal = () => {
    if (!showConfig) return null;

    return (
      <div className="config-overlay">
        <div className="config-modal">
          <div className="config-header">
            <h3>API Configuration</h3>
            <button onClick={() => setShowConfig(false)}>✕</button>
          </div>
          
          <div className="config-content">
            <div className="config-field">
              <label>Anthropic API Key (Required)</label>
              <input
                type="password"
                value={apiKeys.anthropic}
                onChange={(e) => setApiKeys(prev => ({...prev, anthropic: e.target.value}))}
                placeholder="sk-ant-..."
              />
            </div>
            
            <div className="config-field">
              <label>Serper API Key (Optional - for search)</label>
              <input
                type="password"
                value={apiKeys.serper}
                onChange={(e) => setApiKeys(prev => ({...prev, serper: e.target.value}))}
                placeholder="Your Serper API key..."
              />
            </div>
            
            <div className="config-actions">
              <div style={{display: 'flex', gap: '10px'}}>
                <button onClick={testApiKey} className="save-button" style={{backgroundColor: '#4CAF50'}}>
                  Test API Key
                </button>
                <button onClick={saveApiKeys} className="save-button">
                  Save Configuration
                </button>
              </div>
            </div>
            
            <div className="config-help">
              <p>Get your API keys:</p>
              <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer">
                Anthropic Console
              </a>
              <a href="https://serper.dev" target="_blank" rel="noopener noreferrer">
                Serper.dev
              </a>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderResourcesModal = () => {
    if (!showResources || accumulatedResources.length === 0) return null;

    return (
      <div className="resources-modal-overlay">
        <div className="resources-modal">
          <div className="resources-modal-header">
            <h3>Found Resources ({accumulatedResources.length})</h3>
            <button onClick={() => setShowResources(false)}>✕</button>
          </div>
          
          <div className="resources-modal-content">
            <div className="resources-list">
              {accumulatedResources.map((resource, index) => (
                <div key={index} className="resource-item">
                  <div className="resource-category">{resource.category}</div>
                  <div className="resource-title">{resource.name}</div>
                  
                  <div className="resource-links">
                    {resource.url && (
                      <a 
                        href={resource.url.startsWith('http') ? resource.url : `https://${resource.url}`} 
                        className="resource-url" 
                        target="_blank" 
                        rel="noopener noreferrer"
                      >
                        🌐 {resource.url.replace(/^https?:\/\//, '')}
                      </a>
                    )}
                    {resource.contact && resource.contact.includes('(') && (
                      <a 
                        href={`tel:${resource.contact.replace(/\D/g, '')}`}
                        className="resource-url"
                      >
                        📞 {resource.contact}
                      </a>
                    )}
                  </div>
                  
                  <div className="resource-description">{resource.description}</div>
                  
                  {resource.next_step && (
                    <div className="resource-next-step">
                      <strong>→ Next Step: </strong>{resource.next_step}
                    </div>
                  )}
                  
                  <div className="resource-meta">
                    {resource.location && (
                      <span className="meta-item">📍 {resource.location}</span>
                    )}
                    {resource.hours && (
                      <span className="meta-item">🕒 {resource.hours}</span>
                    )}
                    {resource.eligibility && (
                      <span className="meta-item">✓ {resource.eligibility}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderThinkingLogModal = () => {
    if (thinkingLogCollapsed || allStreamingEvents.length === 0) return null;

    return (
      <div className="resources-modal-overlay">
        <div className="resources-modal">
          <div className="resources-modal-header">
            <h3>Agent Thinking Log ({allStreamingEvents.length} conversations)</h3>
            <button onClick={() => setThinkingLogCollapsed(true)}>✕</button>
          </div>
          
          <div className="resources-modal-content">
            <div style={{ fontFamily: 'Space Mono, monospace', maxHeight: '60vh', overflowY: 'auto' }}>
              {allStreamingEvents.map((session, sessionIndex) => (
                <div key={sessionIndex} style={{ 
                  marginBottom: '24px', 
                  border: '1px solid var(--border)', 
                  background: 'var(--bg-tertiary)',
                  borderRadius: '8px',
                  padding: '16px'
                }}>
                  <div style={{ 
                    color: 'var(--text-secondary)', 
                    fontSize: '12px', 
                    marginBottom: '12px',
                    textTransform: 'uppercase',
                    letterSpacing: '1px'
                  }}>
                    Session {sessionIndex + 1} • {session.timestamp}
                  </div>
                  
                  {session.events.map((event, eventIndex) => (
                    <div key={eventIndex} style={{
                      padding: '8px 12px',
                      margin: '4px 0',
                      background: 'var(--bg-secondary)',
                      border: '1px solid var(--border)',
                      borderRadius: '4px',
                      fontSize: '13px',
                      lineHeight: '1.4'
                    }}>
                      <span style={{ color: 'var(--accent-blue)' }}>•</span> {event}
                    </div>
                  ))}
                </div>
              ))}
              
              <div style={{ 
                marginTop: '24px', 
                padding: '16px', 
                background: 'var(--bg-secondary)', 
                fontSize: '11px', 
                color: 'var(--text-muted)',
                textAlign: 'center'
              }}>
                💡 This log shows the AI agent's step-by-step thinking process for transparency and debugging
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderPerformanceModal = () => {
    if (!showPerformance || !performanceData) return null;

    const stepNames: {[key: string]: string} = {
      'initialize_context': 'Initialize Context',
      'decide_strategy': 'Analyze Message & Decide Strategy',
      'search_resources': 'Search for Resources',
      'generate_response': 'Generate Final Response'
    };

    return (
      <div className="resources-modal-overlay">
        <div className="resources-modal">
          <div className="resources-modal-header">
            <h3>Performance Monitor</h3>
            <button onClick={() => setShowPerformance(false)}>✕</button>
          </div>
          
          <div className="resources-modal-content">
            <div style={{ fontFamily: 'Space Mono, monospace' }}>
              <div style={{ marginBottom: '24px', padding: '16px', background: 'var(--bg-tertiary)', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '8px' }}>TOTAL EXECUTION TIME</div>
                <div style={{ fontSize: '24px', color: 'var(--text-primary)', fontWeight: '600' }}>
                  {performanceData.execution_time_ms}ms
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  {performanceData.execution_time_ms && performanceData.execution_time_ms < 5000 ? 
                    '🟢 FAST' : performanceData.execution_time_ms && performanceData.execution_time_ms < 10000 ? 
                    '🟡 MODERATE' : '🔴 SLOW'}
                </div>
              </div>

              {performanceData.step_timings && (
                <div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '16px', letterSpacing: '2px', textTransform: 'uppercase' }}>
                    STEP BREAKDOWN
                  </div>
                  
                  {Object.entries(performanceData.step_timings).map(([step, duration]) => {
                    const percentage = performanceData.execution_time_ms ? 
                      ((duration * 1000) / performanceData.execution_time_ms * 100).toFixed(1) : '0';
                    
                    return (
                      <div key={step} style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'center',
                        padding: '12px 0',
                        borderBottom: '1px solid var(--border)'
                      }}>
                        <div>
                          <div style={{ color: 'var(--text-primary)', fontSize: '14px' }}>
                            {stepNames[step] || step}
                          </div>
                          <div style={{ color: 'var(--text-muted)', fontSize: '10px', marginTop: '2px' }}>
                            {percentage}% of total time
                          </div>
                        </div>
                        <div style={{ 
                          color: 'var(--accent-blue)', 
                          fontSize: '16px',
                          fontWeight: '600'
                        }}>
                          {Math.round(duration * 1000)}ms
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              <div style={{ marginTop: '24px', padding: '16px', background: 'var(--bg-secondary)', fontSize: '11px', color: 'var(--text-muted)' }}>
                <div style={{ marginBottom: '8px', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                  Performance Notes
                </div>
                <div style={{ lineHeight: '1.6' }}>
                  • Initialize Context: Loading conversation history, setting up temporal context<br/>
                  • Analyze & Decide: AI agent categorizes need and decides if search is required<br/>
                  • Search Resources: Finding relevant civic resources (skipped for greetings)<br/>
                  • Generate Response: Creating final conversational response with empathy
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="civic-app">
      <div className="status-bar">
        SYSTEM STATUS: <span className={backendConnected ? 'status-connected' : 'status-error'}>
          {backendConnected ? 'CONNECTED' : 'DISCONNECTED'}
        </span>
        {apiKeys.anthropic ? (
          <>
            <span className="status-connected"> • API CONFIGURED</span>
            <button onClick={() => setShowConfig(true)} className="config-button" style={{marginLeft: '10px'}}>
              EDIT KEYS
            </button>
          </>
        ) : (
          <button onClick={() => setShowConfig(true)} className="config-button">
            CONFIGURE API KEYS
          </button>
        )}
        {performanceData?.execution_time_ms && (
          <>
            <span className="status-connected"> • LAST RESPONSE: {performanceData.execution_time_ms}ms</span>
            <button onClick={() => setShowPerformance(true)} className="config-button" style={{ marginLeft: '8px' }}>
              VIEW BREAKDOWN
            </button>
          </>
        )}
        {allStreamingEvents.length > 0 && (
          <button onClick={() => setThinkingLogCollapsed(!thinkingLogCollapsed)} className="config-button" style={{ marginLeft: '8px' }}>
            THINKING LOG ({allStreamingEvents.length})
          </button>
        )}
      </div>

      <header>
        <div className="logo">CIVIC<span>_</span>RESOURCE<span>_</span>AGENT</div>
        <div className="location">PEORIA, IL</div>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <label style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
            <input 
              type="checkbox" 
              checked={streamingMode}
              onChange={(e) => setStreamingMode(e.target.checked)}
              style={{ marginRight: '8px' }}
            />
            STREAMING MODE
          </label>
          {showStreamingPanel && (
            <button 
              onClick={() => setShowStreamingPanel(!showStreamingPanel)}
              className="config-button"
            >
              SHOW THINKING
            </button>
          )}
        </div>
      </header>

      <main>
        <section className="chat-panel-full">
          <div className="panel-label">
            Query
          </div>
          
          <div className="chat-messages">
            {messages.map((message, index) => (
              <div key={index} className={`message ${message.role}`}>
                <div className="message-text">
                  {message.role === 'agent' ? (
                    <ReactMarkdown
                      components={{
                        a: ({ href, children }) => (
                          <a 
                            href={href} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            style={{ 
                              color: 'var(--accent-blue)', 
                              textDecoration: 'underline',
                              wordBreak: 'break-all'
                            }}
                          >
                            {children}
                          </a>
                        )
                      }}
                    >
                      {linkifyMarkdown(message.content)}
                    </ReactMarkdown>
                  ) : (
                    <span>{linkifyText(message.content)}</span>
                  )}
                </div>
                <div className="message-time">{message.timestamp}</div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message agent">
                {streamingMode && streamingEvents.length > 0 ? (
                  <div className="streaming-container">
                    <div className="streaming-header">
                      <strong>🤖 Agent Thinking Process:</strong>
                    </div>
                    {streamingEvents.map((event, index) => (
                      <div key={index} className="streaming-event">
                        {event}
                      </div>
                    ))}
                    <div className="loading">
                      <div className="loading-dot"></div>
                      <div className="loading-dot"></div>
                      <div className="loading-dot"></div>
                    </div>
                  </div>
                ) : (
                  <div className="loading">
                    <div className="loading-dot"></div>
                    <div className="loading-dot"></div>
                    <div className="loading-dot"></div>
                  </div>
                )}
                <div className="message-time">{getCurrentTime()}</div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Agent Thinking Panel - Above Chat Input */}
          {(isLoading || streamingEvents.length > 0) && (
            <div className="thinking-panel">
              <div className="thinking-header">
                🤖 Agent Thinking Process
                <div className="thinking-controls">
                  <div className="thinking-status">
                    {isLoading ? "Processing..." : "Complete"}
                  </div>
                  <button 
                    className="thinking-expand-btn"
                    onClick={() => setThinkingPanelExpanded(!thinkingPanelExpanded)}
                    title={thinkingPanelExpanded ? "Collapse details" : "Expand details"}
                  >
                    {thinkingPanelExpanded ? "−" : "+"}
                  </button>
                  {!isLoading && streamingEvents.length > 0 && (
                    <button 
                      className="thinking-clear-btn"
                      onClick={() => setStreamingEvents([])}
                      title="Clear thinking process"
                    >
                      ✕
                    </button>
                  )}
                </div>
              </div>
              
              {/* Collapsed view - just show summary */}
              {!thinkingPanelExpanded ? (
                <div className="thinking-content-collapsed">
                  <div className="thinking-summary" style={{
                    fontSize: '12px',
                    color: 'var(--text-secondary)',
                    fontFamily: 'inherit',
                    padding: '8px 16px'
                  }}>
                    {isLoading ? "Processing your request..." : 
                     streamingEvents.length > 0 ? `Completed ${streamingEvents.length} steps` : "Ready"}
                  </div>
                </div>
              ) : (
                /* Expanded view - show all details */
                <div className="thinking-content">
                  {streamingEvents.length > 0 ? (
                    streamingEvents.map((event, index) => (
                      <div key={index} className="thinking-step">
                        <div className="thinking-step-icon">•</div>
                        <div className="thinking-step-text">{event}</div>
                      </div>
                    ))
                  ) : (
                    <div className="thinking-step">
                      <div className="thinking-step-icon">⏳</div>
                      <div className="thinking-step-text">Analyzing your request...</div>
                    </div>
                  )}
                  {isLoading && (
                    <div className="thinking-step thinking-active">
                      <div className="loading-dots">
                        <div className="dot"></div>
                        <div className="dot"></div>
                        <div className="dot"></div>
                      </div>
                      <div className="thinking-step-text">Working...</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          <div className="chat-input-container">
            <input
              ref={inputRef}
              type="text"
              className="chat-input"
              placeholder="Ask about local resources, services, programs..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <div className="input-hint">
              Press <kbd>ENTER</kbd> to search
            </div>
          </div>
        </section>
        
        {/* Persistent Resources Panel */}
        <section className="results-panel">
          <div className="results-header">
            <div className="panel-label">
              Found Resources ({accumulatedResources.length})
            </div>
          </div>
          
          <div className="results-list">
            {accumulatedResources.length === 0 ? (
              <div style={{ 
                textAlign: 'center', 
                color: 'var(--text-muted)', 
                padding: '40px 20px',
                fontSize: '14px'
              }}>
                Resources found by the AI agent will appear here as you chat
              </div>
            ) : (
              accumulatedResources.map((resource, index) => (
              <div key={index} className="result-item">
                <div className="result-category">{resource.category}</div>
                <div className="result-title">{resource.name}</div>
                
                <div className="resource-links" style={{ display: 'flex', gap: '16px', marginBottom: '16px', flexWrap: 'wrap' }}>
                  {resource.url && (
                    <a 
                      href={resource.url.startsWith('http') ? resource.url : `https://${resource.url}`} 
                      className="result-url" 
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      🌐 {resource.url.replace(/^https?:\/\//, '')}
                    </a>
                  )}
                  {resource.contact && resource.contact.includes('(') && (
                    <a 
                      href={`tel:${resource.contact.replace(/\D/g, '')}`}
                      className="result-url"
                    >
                      📞 {resource.contact}
                    </a>
                  )}
                </div>
                
                <div className="result-description">{resource.description}</div>
                
                {resource.next_step && (
                  <div className="result-next-step">
                    <strong>→ Next Step: </strong>{resource.next_step}
                  </div>
                )}
                
                <div className="result-meta">
                  {resource.location && (
                    <span className="meta-item">📍 {resource.location}</span>
                  )}
                  {resource.hours && (
                    <span className="meta-item">🕒 {resource.hours}</span>
                  )}
                  {resource.eligibility && (
                    <span className="meta-item">✓ {resource.eligibility}</span>
                  )}
                </div>
              </div>
            ))
            )}
          </div>
        </section>
      </main>

      <footer>
        <div className="footer-left">
          Built by <a href="https://the-aicollective.slack.com" target="_blank" rel="noopener noreferrer">AI Collective Peoria</a> — MIT License
        </div>
        <div className="footer-right">
          <button onClick={() => setShowConfig(true)} className="footer-link">
            Configure
          </button>
          <a href="https://github.com/thecuriousnobody/civic-problem-solver" target="_blank" rel="noopener noreferrer" className="footer-link">
            GitHub
          </a>
          <a href="#" className="footer-link">How It Works</a>
        </div>
      </footer>

      {renderConfigModal()}
      {renderThinkingLogModal()}
      {renderPerformanceModal()}
    </div>
  );
};

export default CivicResourceAgent;