from proj4 import *
import unittest


class TestStateSearch(unittest.TestCase):

    def setUp(self): 
        search(secrets.API_KEY, 'lunch', 'ann arbor, MI')
        search_2(secrets.API_KEY, 'lunch', 'ann arbor, MI')


    def test_Yelp(self):
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        sql = '''
            SELECT COUNT(*)
            FROM Yelp
        '''
        results = cur.execute(sql)
        count = results.fetchone()[0]
        self.assertTrue(count > 99) #1

        sql = '''
            SELECT RestaurantName, State
            FROM Yelp
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('eat', 'MI'), result_list) #2
        self.assertEqual(result_list[0][1], 'MI') #3
        self.assertEqual(type(result_list[0][1]), str) #4

        con.close()

    def test_Tripadvisor(self):
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        sql = '''
            SELECT RestaurantName
            FROM Tripadvisor
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('The Lunch Room',), result_list) #5
        self.assertEqual(len(result_list), 30) #6

        sql = '''
            SELECT RestaurantName, Rating, Cuisine
            FROM Tripadvisor
            WHERE RestaurantName = 'Mani Osteria'
        '''
        results = cur.execute(sql)
        result_list = results.fetchall() 
        self.assertEqual(result_list[0][1], 4.5) #7
        self.assertEqual(result_list[0][2], 'Italian') #8
        self.assertEqual(result_list[0][0], 'Mani Osteria') #9
        self.assertEqual(type(result_list[0][1]), float) #10

        con.close()


    def test_files(self):
        self.assertEqual(type(CACHE_FNAME_1), str) #11
        
    def test_show_plot_gauzechart(self):
        try:
            get_from_trip_results('The Lunch Room', 4.5) #12
        except:
            self.fail()

    def test_show_plot_map(self):
        try:
            plot_map_restaurant('The Lunch Room') #13
        except:
            self.fail()

    def test_show_plot_rating(self):
        try:
            plot_gauzechart_rating([4, 4.5]) #14
        except:
            self.fail()

    def test_show_plot_barchart(self):
        try:
            plot_barchart_cuisine() #15
        except:
            self.fail()

    def test_show_plot_piechart(self):
        try:
            plot_piechart_cuisine() #16
        except:
            self.fail()



if __name__ == '__main__':
    unittest.main(verbosity=2)

