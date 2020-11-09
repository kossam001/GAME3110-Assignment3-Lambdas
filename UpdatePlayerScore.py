import json
import boto3
import decimal

def calculateRatings(p1Score, p2Score):
    return 1 / (1 + pow(10, (p1Score - p2Score)/400))

def lambda_handler(event, context):
    
    db = boto3.resource("dynamodb")
    table = db.Table("Assignment3DB")
    
    if 'body' in event:
        
        # Content of body: {players: [{'user_id' : '#', 'score' : 'score#''}], results: {'id#' : 'win'/'lose'}}
        data = json.loads(event['body'])
        
        # Get the information on the players
        players = data['players']
        
        # Get the results of the match
        matchResults = data['results']
        
        # Get ratings before they are updated
        tempRatingScore = {}
        for player in players:
            tempRatingScore[player['user_id']] = player['score']
        
        # Calculate ratings for each player
        # Winner gets 1 score for each lose player
        # Lose player gets 0.5 score for another lose player and 0 score for win player
        for p1 in players:
            if matchResults[p1['user_id']] == 'win':
                p1['wins'] = str(int(p1['wins']) + 1)
            else:
                p1['losses'] = str(int(p1['losses']) + 1)
            
            for p2 in players:
                
                # Make sure that we are not checking the same player
                if p1['user_id'] != p2['user_id']:
                    winOdds = calculateRatings(float(tempRatingScore[p1['user_id']]), float(tempRatingScore[p2['user_id']]))
                    
                    if matchResults[p1['user_id']] == 'win':
                        
                        ratingChange = (1 - winOdds) * 100
                        
                        # Add to current rating score
                        currentRating = float(p1['score'])
                        p1['score'] = str(int(currentRating + ratingChange))
                        
                    elif matchResults[p1['user_id']] == 'lose':
                        
                        if matchResults[p2['user_id']] == 'lose':
                            
                            ratingChange = (0.5 - winOdds) * 100
                        
                            # Add to current rating score
                            currentRating = float(p1['score'])
                            p1['score'] = str(int(currentRating + ratingChange))
                            
                        elif matchResults[p2['user_id']] == 'win':
                            
                            ratingChange = (0 - winOdds) * 100
                        
                            # Add to current rating score
                            currentRating = float(p1['score'])
                            p1['score'] = str(int(currentRating + ratingChange))
    
        print(tempRatingScore)
        print(" ")
        print(players)
        
        response = {}
        response['matchId'] = str(data['matchId'])
        response['players'] = players
    
        for player in players:
            table.update_item(
                Key={
                    'user_id': player["user_id"]
                },
                UpdateExpression='SET wins = :val1, losses = :val2, score = :val3',
                ExpressionAttributeValues={
                    ':val1': player['wins'],
                    ':val2': player['losses'],
                    ':val3': player['score']
                }
            )
        
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }