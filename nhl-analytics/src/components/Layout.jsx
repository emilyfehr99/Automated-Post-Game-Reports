import React from 'react';
import Navbar from './Navbar';
import LiveGameTicker from './LiveGameTicker';
import { motion } from 'framer-motion';

const Layout = ({ children }) => {
    return (
        <div className="min-h-screen relative selection:bg-accent-primary/30 selection:text-white">
            {/* Ambient Background Effects */}
            <div className="fixed inset-0 pointer-events-none z-0">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-accent-primary/5 rounded-full blur-[120px] animate-pulse-slow" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent-secondary/5 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
                <div className="absolute inset-0 bg-grid-pattern opacity-20" />
            </div>

            <div className="fixed top-0 left-0 right-0 z-50">
                <LiveGameTicker />
                <Navbar />
            </div>

            <main className="relative z-10 pt-40 pb-12 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                >
                    {children}
                </motion.div>
            </main>

            <footer className="relative z-10 border-t border-white/5 bg-bg-secondary/50 backdrop-blur-sm py-8 mt-auto">
                <div className="max-w-7xl mx-auto px-4 text-center">
                    <p className="font-mono text-xs text-text-muted uppercase tracking-widest">
                        &copy; {new Date().getFullYear()} PuckAnalytics • Data via NHL API
                    </p>
                </div>
            </footer>
        </div>
    );
};

export default Layout;
