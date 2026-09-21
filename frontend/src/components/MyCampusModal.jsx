import React, { useState, useEffect } from 'react';
import { X, UserCheck, GraduationCap, Users, Sparkles, Check } from 'lucide-react';

const DEPARTMENTS = [
  'Computer Science and Engineering (CSE)',
  'Artificial Intelligence & Data Science (AI&DS)',
  'Biotechnology',
  'Electronics & Communication Engineering (ECE)',
  'Electrical & Electronics Engineering (EEE)',
  'Mechanical Engineering',
  'Civil Engineering',
  'Information Technology'
];

const INTERESTS_LIST = [
  'AI & Machine Learning',
  'Drones & Robotics',
  'Hackathons & Coding',
  'Placement & Interviews',
  'Hostel & Mess',
  'Admissions & Fees',
  'Sports & Culturals',
  'Academic Regulations'
];

export default function MyCampusModal({ isOpen, onClose, onProfileSaved }) {
  const [role, setRole] = useState('current_student');
  const [department, setDepartment] = useState('');
  const [year, setYear] = useState('');
  const [semester, setSemester] = useState('');
  const [selectedInterests, setSelectedInterests] = useState([]);

  useEffect(() => {
    if (isOpen) {
      try {
        const saved = JSON.parse(localStorage.getItem('campusiq_profile') || '{}');
        if (saved.role) setRole(saved.role);
        if (saved.department) setDepartment(saved.department);
        if (saved.year) setYear(saved.year);
        if (saved.semester) setSemester(saved.semester);
        if (saved.interests) setSelectedInterests(saved.interests);
      } catch (e) {}
    }
  }, [isOpen]);

  const toggleInterest = (interest) => {
    setSelectedInterests(prev =>
      prev.includes(interest) ? prev.filter(i => i !== interest) : [...prev, interest]
    );
  };

  const handleSave = () => {
    const profile = {
      role,
      department: role === 'current_student' ? department : '',
      year: role === 'current_student' ? year : '',
      semester: role === 'current_student' ? semester : '',
      interests: selectedInterests
    };
    localStorage.setItem('campusiq_profile', JSON.stringify(profile));
    if (onProfileSaved) onProfileSaved(profile);
    onClose();
  };

  const handleClear = () => {
    localStorage.removeItem('campusiq_profile');
    setRole('current_student');
    setDepartment('');
    setYear('');
    setSemester('');
    setSelectedInterests([]);
    if (onProfileSaved) onProfileSaved(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.55)',
        backdropFilter: 'blur(4px)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px'
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: '100%',
          maxWidth: '620px',
          maxHeight: '90vh',
          backgroundColor: 'var(--bg-card)',
          borderRadius: 'var(--radius-lg)',
          border: '1.5px solid var(--border-subtle)',
          boxShadow: 'var(--shadow-lg)',
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <div style={{
          padding: '20px 24px 14px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              backgroundColor: 'var(--accent-burgundy-light)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-burgundy)'
            }}>
              <UserCheck size={22} />
            </div>
            <div>
              <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: '1.24rem',
                fontWeight: 700,
                color: 'var(--accent-burgundy)',
                margin: 0
              }}>
                My Campus Personalization
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0 }}>
                Tailor suggestions and quick navigation for your background. Optional for all users.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              padding: '4px'
            }}
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>

        {/* Form Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {/* Role Choice */}
          <div>
            <label style={fieldLabelStyle}>I am a:</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
              {[
                { id: 'current_student', label: 'Current PEC Student', icon: GraduationCap },
                { id: 'prospective_student', label: 'Prospective Student / Parent / Visitor', icon: Users }
              ].map(item => {
                const Icon = item.icon;
                const isSelected = role === item.id;
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setRole(item.id)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '10px 14px',
                      borderRadius: 'var(--radius-sm)',
                      border: isSelected ? '1.5px solid var(--accent-burgundy)' : '1px solid var(--border-subtle)',
                      backgroundColor: isSelected ? 'var(--accent-burgundy-light)' : 'var(--bg-card-subtle)',
                      color: isSelected ? 'var(--accent-burgundy)' : 'var(--text-primary)',
                      fontWeight: 600,
                      fontSize: '0.82rem',
                      cursor: 'pointer',
                      textAlign: 'left'
                    }}
                  >
                    <Icon size={16} />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Student Fields */}
          {role === 'current_student' && (
            <>
              <div>
                <label style={fieldLabelStyle}>Department:</label>
                <select
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  style={selectStyle}
                >
                  <option value="">Select your department (optional)</option>
                  {DEPARTMENTS.map((dept, i) => (
                    <option key={i} value={dept}>{dept}</option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                <div>
                  <label style={fieldLabelStyle}>Academic Year:</label>
                  <select
                    value={year}
                    onChange={(e) => setYear(e.target.value)}
                    style={selectStyle}
                  >
                    <option value="">Select Year</option>
                    <option value="1st Year">1st Year</option>
                    <option value="2nd Year">2nd Year</option>
                    <option value="3rd Year">3rd Year</option>
                    <option value="4th Year">4th Year</option>
                  </select>
                </div>

                <div>
                  <label style={fieldLabelStyle}>Semester:</label>
                  <select
                    value={semester}
                    onChange={(e) => setSemester(e.target.value)}
                    style={selectStyle}
                  >
                    <option value="">Select Semester</option>
                    {[1, 2, 3, 4, 5, 6, 7, 8].map(s => (
                      <option key={s} value={`Semester ${s}`}>Semester {s}</option>
                    ))}
                  </select>
                </div>
              </div>
            </>
          )}

          {/* Interests */}
          <div>
            <label style={fieldLabelStyle}>Key Topics of Interest:</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {INTERESTS_LIST.map(interest => {
                const isSelected = selectedInterests.includes(interest);
                return (
                  <button
                    key={interest}
                    type="button"
                    onClick={() => toggleInterest(interest)}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '5px 12px',
                      borderRadius: 'var(--radius-full)',
                      border: isSelected ? '1px solid var(--accent-burgundy)' : '1px solid var(--border-subtle)',
                      backgroundColor: isSelected ? 'var(--accent-burgundy)' : 'var(--bg-card-subtle)',
                      color: isSelected ? '#FFFFFF' : 'var(--text-secondary)',
                      fontSize: '0.78rem',
                      fontWeight: 500,
                      cursor: 'pointer'
                    }}
                  >
                    {isSelected && <Check size={12} />}
                    <span>{interest}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Strict Anti-Fabrication Notice */}
          <div style={{
            padding: '10px 14px',
            backgroundColor: 'var(--bg-card-subtle)',
            borderRadius: '6px',
            border: '1px solid var(--border-subtle)',
            fontSize: '0.74rem',
            color: 'var(--text-muted)',
            lineHeight: 1.4
          }}>
            <strong>Integrity Promise:</strong> CampusIQ uses your profile only to highlight relevant sections and verified navigation links. It will <em>never</em> invent your personal timetable, attendance records, exam marks, or deadlines.
          </div>
        </div>

        {/* Footer */}
        <div style={{
          padding: '14px 24px',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <button
            onClick={handleClear}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              fontSize: '0.80rem',
              cursor: 'pointer'
            }}
          >
            Reset Profile
          </button>

          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={onClose}
              style={{
                padding: '8px 16px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--border-subtle)',
                backgroundColor: 'transparent',
                color: 'var(--text-primary)',
                fontSize: '0.82rem',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              style={{
                padding: '8px 18px',
                borderRadius: 'var(--radius-sm)',
                border: 'none',
                backgroundColor: 'var(--accent-burgundy)',
                color: '#FFFFFF',
                fontSize: '0.82rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Save Preferences
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

const fieldLabelStyle = {
  display: 'block',
  fontSize: '0.80rem',
  fontWeight: 600,
  color: 'var(--text-primary)',
  marginBottom: '6px'
};

const selectStyle = {
  width: '100%',
  padding: '8px 12px',
  borderRadius: '6px',
  border: '1px solid var(--border-subtle)',
  backgroundColor: 'var(--bg-card-subtle)',
  color: 'var(--text-primary)',
  fontSize: '0.82rem',
  outline: 'none'
};
