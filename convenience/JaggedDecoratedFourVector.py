import awkward
import uproot_methods

JaggedWithLorentz = awkward.Methods.mixin(uproot_methods.classes.TLorentzVector.ArrayMethods, awkward.JaggedArray)

class JaggedDecoratedFourVector(awkward.JaggedArray,):
    def __init__(self,jagged):        
        super(JaggedDecoratedFourVector, self).__init__(jagged.starts,
                                                        jagged.stops,
                                                        jagged.content)
        self._ispair = False
        self._iscross = False
        if hasattr(jagged,'_ispair'):
            self._ispair = jagged._ispair
        if hasattr(jagged,'_iscross'):
            self._iscross = jagged._iscross
    
    @classmethod
    def fromcounts(cls,counts,p4,**kwargs):
        the_p4 = p4
        if not isinstance(p4,uproot_methods.TLorentzVectorArray):
            the_p4 = uproot_methods.TLorentzVectorArray(p4[:,0],p4[:,1],p4[:,2],p4[:,3])
        items = {'p4':the_p4}
        items.update(kwargs)
        return JaggedDecoratedFourVector(awkward.JaggedArray.fromcounts(counts,awkward.Table(items)))
    
    def pairs(self, same=True):
        outs = JaggedDecoratedFourVector(super(JaggedDecoratedFourVector, self).pairs(same))
        outs['p4'] = outs._0.p4 + outs._1.p4
        outs._ispair = True
        return outs
    
    def cross(self, other):
        outs = JaggedDecoratedFourVector(super(JaggedDecoratedFourVector, self).cross(other))
        #currently JaggedArray.cross() has some funny behavior when it encounters the
        # p4 column and make some wierd new column... for now I just delete it and reorder
        # everything looks ok after that
        if outs._iscross:
            keys = outs.columns
            for key in keys:
                if not isinstance(outs[key].content,awkward.array.table.Table):
                    del outs[key]
            keys = outs.columns
            realkey = {}
            for i in xrange(len(keys)):
                realkey[keys[i]] = str(i)
            for key in keys:
                if realkey[key] != key:
                    outs[realkey[key]] = outs[key]
                    del outs[key]
            keys = outs.columns
            for key in keys:                    
                if 'p4' not in outs.columns:
                    outs['p4'] = outs[key].p4
                else:
                    outs['p4'] = outs.p4 + outs[key].p4
        else:
            outs['p4'] = outs._0.p4 + outs._1.p4
            outs._iscross = True
        return outs
    
    def __getattr__(self,what):
        #print('-getattr-what   :',what)
        #print('-getattr-content:',type(self.content))
        toget = what
        if not isinstance(self.content,awkward.array.table.Table):
            return awkward.JaggedArray.fromcounts(self.counts,getattr(self.content,toget))
        if what[0] == "_" and what[1:].isdigit(): toget = what[1:]
        return super(JaggedDecoratedFourVector, self).__getitem__(toget)
