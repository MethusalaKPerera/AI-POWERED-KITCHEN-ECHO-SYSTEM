import React, { useState, useEffect, useRef } from 'react';
import './LanguageSelector.css';

const LANGUAGES = [
    { code: 'en', label: 'English', native: 'English', flag: '🇬🇧' },
    { code: 'si', label: 'Sinhala', native: 'සිංහල', flag: '🇱🇰' },
    { code: 'ta', label: 'Tamil', native: 'தமிழ்', flag: '🇱🇰' },
];

function loadGoogleTranslate() {
    if (window._gtLoaded) return;
    window._gtLoaded = true;
    window.googleTranslateElementInit = function () {
        new window.google.translate.TranslateElement(
            { pageLanguage: 'en', includedLanguages: 'en,si,ta', autoDisplay: false },
            'gt_hidden_el'
        );
    };
    const s = document.createElement('script');
    s.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    s.async = true;
    document.body.appendChild(s);
}

function LanguageSelector() {
    const [open, setOpen] = useState(false);
    const [active, setActive] = useState(LANGUAGES[0]);
    const ref = useRef(null);

    useEffect(() => {
        loadGoogleTranslate();
        const close = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
        document.addEventListener('mousedown', close);
        return () => document.removeEventListener('mousedown', close);
    }, []);

    const switchLang = (lang) => {
        setActive(lang);
        setOpen(false);
        const select = document.querySelector('.goog-te-combo');
        if (select) {
            select.value = lang.code;
            select.dispatchEvent(new Event('change'));
        }
    };

    return (
        <div className="ls-block">
            <div id="gt_hidden_el" style={{ display: 'none' }}></div>
            <div className="ls-selector" ref={ref}>
                <button className="ls-btn" onClick={() => setOpen(o => !o)}>
                    <span className="ls-flag">{active.flag}</span>
                    <span className="ls-label">{active.label}</span>
                    <span className={`ls-arrow ${open ? 'open' : ''}`}>▲</span>
                </button>
                {open && (
                    <div className="ls-dropdown">
                        {LANGUAGES.map(lang => (
                            <button
                                key={lang.code}
                                className={`ls-option ${active.code === lang.code ? 'active' : ''}`}
                                onClick={() => switchLang(lang)}
                            >
                                <span className="ls-opt-flag">{lang.flag}</span>
                                <span className="ls-opt-text">
                                    {lang.label}
                                    <span className="ls-opt-native"> — {lang.native}</span>
                                </span>
                                {active.code === lang.code && <span className="ls-check">✓</span>}
                            </button>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

export default LanguageSelector;