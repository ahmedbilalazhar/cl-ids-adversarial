import unittest
import numpy as np

from src.phase3.reference import new_client
from src.phase3_v2.eviction import insert_with_eviction


def memory(labels):
    m = new_client(11, 0)
    m['size'] = len(labels)
    m['seen'] = len(labels)
    m['y'][:len(labels)] = labels
    m['ids'][:len(labels)] = np.arange(1, len(labels)+1, dtype='<u8')
    m['order'] = np.zeros(500, dtype='<u8')
    m['order'][:len(labels)] = np.arange(len(labels), dtype='<u8')
    return m


class EvictionPolicyTests(unittest.TestCase):
    def test_fifo_evicts_oldest_and_always_inserts(self):
        m=memory([1,1,2]); x=np.ones((1,74),dtype='<f4'); labels=np.array([9]); ids=np.array([99],dtype='<u8')
        teachers=np.zeros((1,3),dtype='<f4')
        nxt=insert_with_eviction(m,x,labels,ids,teachers,3,'fifo',3,capacity=3)
        self.assertEqual(nxt,4)
        self.assertEqual(m['ids'][:3].tolist(),[99,2,3])
        self.assertEqual(m['y'][:3].tolist(),[9,1,2])

    def test_class_balanced_evicts_oldest_from_largest_class(self):
        m=memory([1,1,2,3]); x=np.ones((1,74),dtype='<f4'); labels=np.array([9]); ids=np.array([99],dtype='<u8')
        teachers=np.zeros((1,3),dtype='<f4')
        insert_with_eviction(m,x,labels,ids,teachers,3,'class_balanced',4,capacity=4)
        self.assertEqual(m['ids'][:4].tolist(),[99,2,3,4])

    def test_class_tie_break_uses_smallest_source_code(self):
        m=memory([2,1,2,1]); x=np.ones((1,74),dtype='<f4'); labels=np.array([9]); ids=np.array([99],dtype='<u8')
        teachers=np.zeros((1,3),dtype='<f4')
        insert_with_eviction(m,x,labels,ids,teachers,3,'class_balanced',4,capacity=4)
        self.assertEqual(m['ids'][:4].tolist(),[1,99,3,4])

    def test_rejects_missing_order_state_and_unknown_policy(self):
        m=new_client(11,0)
        with self.assertRaisesRegex(ValueError,'insertion-order'):
            insert_with_eviction(m,np.zeros((0,74)),np.array([],dtype='i8'),np.array([],dtype='u8'),np.zeros((0,3)),3,'fifo',0)
        m['order']=np.zeros(500,dtype='<u8')
        with self.assertRaisesRegex(ValueError,'policy'):
            insert_with_eviction(m,np.zeros((0,74)),np.array([],dtype='i8'),np.array([],dtype='u8'),np.zeros((0,3)),3,'reservoir',0)


if __name__=='__main__': unittest.main()
