import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, User, Receipt, PlusCircle, History } from 'lucide-react';

export default function GroupDashboard() {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center pt-8 px-4">
       <div className="w-full max-w-4xl">
         
         <button 
           onClick={() => navigate('/dashboard')}
           className="group mb-8 flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
         >
           <ArrowLeft size={16} className="group-hover:-translate-x-1 transition-transform" />
           Back to Dashboard
         </button>

         {/* Header area */}
         <div className="flex items-center justify-between bg-slate-900 border border-white/5 p-8 rounded-3xl relative overflow-hidden">
            <div className="absolute right-0 top-0 w-64 h-64 bg-indigo-500/5 blur-[80px] rounded-full pointer-events-none" />
            <div className="relative z-10">
              <h1 className="text-4xl font-extrabold text-white tracking-tight mb-2">Group {id} Dashboard</h1>
              <p className="text-slate-400 font-medium">Keep track of your shared expenses seamlessly.</p>
            </div>
            
            <button className="hidden sm:flex items-center gap-2 bg-white text-slate-950 hover:bg-slate-200 transition-colors px-6 py-3 font-bold rounded-xl active:scale-95 shadow-xl shadow-white/5">
              <PlusCircle size={18} /> Add Expense
            </button>
         </div>

         {/* Stats Grid */}
         <div className="grid grid-cols-2 gap-4 mt-6">
            <div className="bg-slate-900 border border-white/5 p-6 rounded-2xl flex items-center gap-4">
                <div className="p-4 bg-emerald-500/10 rounded-2xl"><Receipt className="text-emerald-400" /></div>
                <div>
                   <p className="text-sm font-medium text-slate-400">Total Group Spending</p>
                   <h2 className="text-3xl font-bold text-white">$1,240.00</h2>
                </div>
            </div>
            <div className="bg-slate-900 border border-white/5 p-6 rounded-2xl flex items-center gap-4">
                <div className="p-4 bg-amber-500/10 rounded-2xl"><History className="text-amber-400" /></div>
                <div>
                   <p className="text-sm font-medium text-slate-400">Total Transactions</p>
                   <h2 className="text-3xl font-bold text-white">4</h2>
                </div>
            </div>
         </div>

       </div>
    </div>
  );
}
