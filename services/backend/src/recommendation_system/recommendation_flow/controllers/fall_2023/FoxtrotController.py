from src.recommendation_system.recommendation_flow.controllers.AbstractController import (
    AbstractController,
)
from src.recommendation_system.recommendation_flow.filtering.fall_2023.FoxtrotFilter import (
    FoxtrotFilter,
)
from src.recommendation_system.recommendation_flow.model_prediction.RandomModel import (
    RandomModel,
)
from src.recommendation_system.recommendation_flow.model_prediction.fall_2023.foxtrot.FoxtrotModel import (
    FoxtrotFeatureGeneration, FoxtrotModel,
)
from src.recommendation_system.recommendation_flow.ranking.fall_2023.FoxtrotRanker import (
    FoxtrotRanker,
)
from src.recommendation_system.recommendation_flow.candidate_generators.foxtrot.TwoTowerANNGenerator import TwoTowerANNGenerator
from src.recommendation_system.recommendation_flow.candidate_generators.foxtrot.CollaberativeFilteredSimilarUsersGenerator import CollaberativeFilteredSimilarUsersGenerator
from src.recommendation_system.recommendation_flow.candidate_generators.ExampleGenerator import (
    ExampleGenerator,
)
from src.recommendation_system.recommendation_flow.shared_data_objects.data_collector import DataCollector
from src.api.metrics.models import TeamName

class FoxtrotController(AbstractController):
    def get_content_ids(self, user_id, limit, offset, seed, starting_point):
        if seed <= 1:  # MySql seeds should be [0, # of rows] not [0, 1]
            seed *= 1000000
        candidate_limit = 100
        candidates, scores = [], []
        generators = []
        if starting_point.get("twoTower", False):
            generators.append(TwoTowerANNGenerator)
        if starting_point.get("collabFilter", False):
            generators.append(CollaberativeFilteredSimilarUsersGenerator)
        if starting_point.get("yourChoice", False):
            generators.append(ExampleGenerator)
        for gen in generators:
           cur_candidates, cur_scores = gen().get_content_ids(
               TeamName.Foxtrot_F2023,
               user_id, candidate_limit, offset, seed, starting_point
           )
           candidates += cur_candidates
           scores += cur_scores if cur_scores else [0] * len(cur_candidates)
        dc = DataCollector()
        dc.gather_data(user_id, candidates)
        filtered_candidates = FoxtrotFilter().filter_ids(
            TeamName.Foxtrot_F2023,
            user_id, candidates, seed, starting_point, dc=dc
        )
        foxtrotFG = FoxtrotFeatureGeneration(dc, filtered_candidates)
        if starting_point.get('randomPredictions'):
            model = RandomModel()
        else:
            model = FoxtrotModel()
        predictions = model.predict_probabilities(
            TeamName.Foxtrot_F2023,
            filtered_candidates,
            user_id,
            seed=seed,
            scores={
                content_id: {"score": score}
                for content_id, score in zip(candidates, scores)
            }
            if scores is not None
            else {},
            fg=foxtrotFG,
        )
        rank = FoxtrotRanker().rank_ids(
            TeamName.Foxtrot_F2023,
            user_id, filtered_candidates, limit, predictions, seed, starting_point, foxtrotFG.X_all
        )
        return rank
