import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import './CivicChat.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  id: string;
}

interface CivicChatResponse {
  response: string;
  session_id: string;
  response_time_ms: number;
  timestamp: string;
  needs_identified: string[];
  user_profile: any;
  follow_up_questions: string[];
  ready_for_matching: boolean;
  resources_found: any[];
  action_plan: any | null;
  conversation_stage: string;
}

const CivicChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "👋 **Welcome to Civic Problem Solver!**\n\nI'm here to help you find local resources and services in your community. Whether you need help with housing, food, transportation, healthcare, employment, or other civic services - I'll guide you to the right programs and show you exactly how to access them.\n\n**What can I help you find today?**",
      timestamp: new Date(),
      id: 'welcome'
    }
  ]);
  
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSessionId] = useState<string>(() => {
    // Generate session ID
    return `civic_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  });
  const [showResourcePanel, setShowResourcePanel] = useState(false);
  const [currentResources, setCurrentResources] = useState<any[]>([]);
  const [currentActionPlan, setCurrentActionPlan] = useState<any>(null);
  const [conversationStage, setConversationStage] = useState<string>('intake');
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Add user message
    const newUserMessage: Message = {
      role: 'user',
      content: userMessage,
      timestamp: new Date(),
      id: `user_${Date.now()}`
    };

    setMessages(prev => [...prev, newUserMessage]);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          session_id: currentSessionId
        })
      });

      if (!response.ok) throw new Error('Failed to send message');

      const data: CivicChatResponse = await response.json();

      // Add assistant response
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        id: `assistant_${Date.now()}`
      };

      setMessages(prev => [...prev, assistantMessage]);
      setConversationStage(data.conversation_stage);

      // Handle resource matching results
      if (data.resources_found && data.resources_found.length > 0) {
        setCurrentResources(data.resources_found);
        setShowResourcePanel(true);
      }

      // Handle action plan
      if (data.action_plan) {
        setCurrentActionPlan(data.action_plan);
      }

    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        role: 'assistant',
        content: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        timestamp: new Date(),
        id: `error_${Date.now()}`
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const renderResourcePanel = () => {
    if (!showResourcePanel || !currentResources.length) return null;

    return (
      <div className="resource-panel">
        <div className="resource-header">
          <h3>📍 Resources Found</h3>
          <button 
            className="close-button"
            onClick={() => setShowResourcePanel(false)}
          >
            ✕
          </button>
        </div>
        
        <div className="resource-list">
          {currentResources.map((resource, index) => (
            <div key={index} className="resource-card">
              <div className="resource-main">
                <h4>{resource.name}</h4>
                <p className="resource-type">{resource.type}</p>
                <div className="resource-services">
                  {resource.services?.map((service: string, idx: number) => (
                    <span key={idx} className="service-tag">{service}</span>
                  ))}
                </div>
              </div>
              
              <div className="eligibility-section">
                <div className={`eligibility-status ${resource.eligibility?.status || 'unknown'}`}>
                  <span className="status-indicator"></span>
                  {resource.eligibility?.status || 'Unknown'} eligibility
                </div>
                
                {resource.eligibility?.next_steps && (
                  <div className="next-steps">
                    <strong>Next Steps:</strong>
                    <ul>
                      {resource.eligibility.next_steps.map((step: string, idx: number) => (
                        <li key={idx}>{step}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              
              <div className="contact-info">
                {resource.contact?.phone && (
                  <a href={`tel:${resource.contact.phone}`} className="contact-button phone">
                    📞 {resource.contact.phone}
                  </a>
                )}
                {resource.contact?.website && (
                  <a href={resource.contact.website} target="_blank" rel="noopener noreferrer" className="contact-button website">
                    🌐 Website
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
        
        {currentActionPlan && (
          <div className="action-plan">
            <h3>🎯 Your Action Plan</h3>
            <ReactMarkdown>{currentActionPlan.summary}</ReactMarkdown>
            
            {currentActionPlan.immediate_steps && currentActionPlan.immediate_steps.length > 0 && (
              <div className="immediate-steps">
                <h4>🚨 Immediate Steps</h4>
                {currentActionPlan.immediate_steps.map((step: any, idx: number) => (
                  <div key={idx} className="action-step">
                    <div className="step-header">
                      <span className="priority-badge">Priority {step.priority}</span>
                      <span className="urgency-badge">{step.urgency}</span>
                    </div>
                    <p><strong>{step.action}</strong></p>
                    <p className="step-time">⏱️ {step.estimated_time}</p>
                  </div>
                ))}
              </div>
            )}
            
            {currentActionPlan.preparation_checklist && (
              <div className="preparation-checklist">
                <h4>📋 Preparation Checklist</h4>
                {currentActionPlan.preparation_checklist.map((item: any, idx: number) => (
                  <div key={idx} className="checklist-item">
                    <input type="checkbox" id={`checklist-${idx}`} />
                    <label htmlFor={`checklist-${idx}`}>
                      <strong>{item.item}</strong> - {item.reason}
                    </label>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="civic-chat-container">
      <div className="civic-chat-main">
        <div className="chat-header">
          <h1>🏛️ Civic Problem Solver</h1>
          <p>Finding local resources made simple</p>
          <div className="stage-indicator">
            Stage: <span className={`stage ${conversationStage}`}>{conversationStage}</span>
          </div>
        </div>

        <div className="messages-container">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-content">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
              <div className="message-timestamp">
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message assistant">
              <div className="message-content loading">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <p>Finding resources for you...</p>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe what kind of help you're looking for..."
            className="message-input"
            disabled={isLoading}
            rows={3}
          />
          <button 
            onClick={sendMessage} 
            disabled={!input.trim() || isLoading}
            className="send-button"
          >
            {isLoading ? '...' : 'Send'}
          </button>
        </div>
      </div>

      {renderResourcePanel()}
    </div>
  );
};

export default CivicChat;