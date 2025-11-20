import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, Trophy, BarChart2, Home } from 'lucide-react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const NavItem = ({ to, icon: Icon, label, active }) => (
    <Link to={to} className="relative group">
        <div className={clsx(
            "flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-300",
            active
                ? "text-white bg-white/10 shadow-lg shadow-white/5"
                : "text-text-secondary hover:text-white hover:bg-white/5"
        )}>
            <Icon size={18} className={clsx(
                "transition-colors duration-300",
                active ? "text-accent-primary" : "group-hover:text-accent-primary"
            )} />
            <span className="font-display tracking-wider text-sm font-medium uppercase">{label}</span>
        </div>
        {active && (
            <motion.div
                layoutId="navbar-indicator"
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent-primary shadow-[0_0_10px_var(--color-accent-primary)]"
                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
            />
        )}
    </Link>
);

const Navbar = () => {
    const location = useLocation();

    return (
        <motion.nav
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            className="flex justify-center pt-4 px-4 pointer-events-none"
        >
            <div className="glass-panel rounded-2xl px-4 py-2 flex items-center gap-4 pointer-events-auto bg-bg-secondary/90 backdrop-blur-xl border-white/10 shadow-2xl">
                <Link to="/" className="flex items-center gap-3 px-4 py-1 mr-2 group border-r border-white/10">
                    <div className="relative">
                        <div className="absolute inset-0 bg-accent-primary/20 blur-lg rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                        <Activity className="h-6 w-6 text-accent-primary transform group-hover:scale-110 transition-transform duration-300" />
                    </div>
                    <div className="flex flex-col leading-none">
                        <span className="font-display font-bold text-lg tracking-tight text-white group-hover:text-accent-primary transition-colors">
                            NHL
                        </span>
                        <span className="font-mono text-[10px] tracking-widest text-text-secondary font-semibold">
                            ANALYTICS
                        </span>
                    </div>
                </Link>

                <div className="flex items-center gap-1">
                    <NavItem to="/" icon={Home} label="Dashboard" active={location.pathname === '/'} />
                    <NavItem to="/metrics" icon={BarChart2} label="Metrics" active={location.pathname === '/metrics'} />
                    <NavItem to="/playoff-race" icon={Trophy} label="Playoffs" active={location.pathname === '/playoff-race'} />
                </div>

                <div className="ml-2 pl-4 border-l border-white/10">
                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-bg-tertiary/50 border border-white/5">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
                        <span className="text-[10px] font-mono text-text-muted font-medium">LIVE</span>
                    </div>
                </div>
            </div>
        </motion.nav>
    );
};

export default Navbar;
