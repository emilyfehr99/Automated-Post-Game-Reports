import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const AnalyticsChart = ({ data, title, dataKey, color = "#00f2ff" }) => {
    if (!data || data.length === 0) return null;

    return (
        <div className="glass-panel p-6 rounded-xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-20 group-hover:opacity-100 transition-opacity">
                <div className="h-2 w-2 rounded-full bg-white animate-pulse"></div>
            </div>

            <h3 className="text-lg font-sans font-bold mb-6 text-white tracking-wider uppercase flex items-center gap-2">
                <span className="w-1 h-6 bg-accent-cyan block"></span>
                {title}
            </h3>

            <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                        <XAxis
                            dataKey="name"
                            stroke="#6b7280"
                            tick={{ fill: '#9ca3af', fontSize: 12, fontFamily: 'JetBrains Mono' }}
                            axisLine={false}
                            tickLine={false}
                        />
                        <YAxis
                            stroke="#6b7280"
                            tick={{ fill: '#9ca3af', fontSize: 12, fontFamily: 'JetBrains Mono' }}
                            axisLine={false}
                            tickLine={false}
                        />
                        <Tooltip
                            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                            contentStyle={{
                                backgroundColor: '#050505',
                                borderColor: 'rgba(255,255,255,0.1)',
                                color: '#fff',
                                fontFamily: 'JetBrains Mono',
                                boxShadow: '0 10px 30px -10px rgba(0,0,0,0.5)'
                            }}
                            itemStyle={{ color: '#fff' }}
                        />
                        <Bar dataKey={dataKey} radius={[2, 2, 0, 0]}>
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={color} className="opacity-80 hover:opacity-100 transition-opacity" />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default AnalyticsChart;
