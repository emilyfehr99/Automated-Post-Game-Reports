import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, Calendar, Trophy, Target } from 'lucide-react';
import { motion } from 'framer-motion';
import clsx from 'clsx';

const NavItem = ({ to, icon: Icon, label, active }) => (
    <Link to={to} className="relative group">
        <div className={clsx(
            "flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-300",
            active ? "text-white bg-white/10" : "text-gray-400 hover:text-white hover:bg-white/5"
        )}>
            <Icon size={18} className={clsx(
                "transition-colors duration-300",
                active ? "text-accent-cyan" : "group-hover:text-accent-cyan"
            )} />
            <span className="font-sans tracking-wider text-sm uppercase font-medium">{label}</span>
        </div>
        {active && (
            <motion.div
                layoutId="navbar-glow"
                className="absolute inset-0 rounded-full bg-accent-cyan/5 blur-md -z-10"
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
            className="fixed top-0 left-0 right-0 z-50 flex justify-center pt-6 px-4"
        >
            <div className="glass-panel rounded-full px-6 py-3 flex items-center gap-8">
                <Link to="/" className="flex items-center gap-2 mr-4 group">
                    <div className="relative">
                        <Activity className="h-6 w-6 text-accent-cyan group-hover:animate-pulse-slow" />
                        <div className="absolute inset-0 bg-accent-cyan/20 blur-lg rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                    <span className="font-sans font-bold text-xl tracking-widest text-white group-hover:text-glow-cyan transition-all">
                        PUCK<span className="text-accent-cyan">ANALYTICS</span>
                    </span>
                </Link>

                <div className="h-6 w-px bg-white/10" />

                <div className="flex items-center gap-2">
                    <NavItem to="/" icon={Calendar} label="Dashboard" active={location.pathname === '/'} />
                    <NavItem to="/todays-action" icon={Target} label="Today's Action" active={location.pathname === '/todays-action'} />
                    <NavItem to="/playoff-race" icon={Trophy} label="Playoff Race" active={location.pathname === '/playoff-race'} />
                    <NavItem to="/metrics" icon={Activity} label="Metrics" active={location.pathname === '/metrics'} />
                </div>
            </div>
        </motion.nav>
    );
};

export default Navbar;
